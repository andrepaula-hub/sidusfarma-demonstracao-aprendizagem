"""Orquestra análise, JSON estrito e gráficos com publicação transacional."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scripts.data_quality.audit import (
    audit_conditional_missingness,
    audit_dataset,
    audit_relationship,
    audit_response_representations,
)
from scripts.data_quality.ingestion import load_datasets, source_fingerprint
from scripts.data_quality.normalization import normalize_datasets
from scripts.data_quality.schema import DATASET_FILES, PRIMARY_KEYS, RELATIONSHIPS
from scripts.metrics.descriptive import (
    describe_categorical,
    describe_numeric,
    describe_temporal,
    detect_iqr_outliers,
)
from scripts.metrics.kpi_calculator import calculate_kpis, compare_granularities
from scripts.visualization.charts import generate_charts


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _generated_at(value: datetime | None) -> str:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.isoformat()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            _json_safe(payload),
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        handle.write("\n")


def _validate_output_contract(payload: dict, contract: str) -> None:
    """Falha antes da publicação quando o envelope versionado está incompleto."""
    common = {
        "schema_version",
        "contract_schema",
        "generated_at",
        "source_fingerprint_sha256",
        "source_manifest",
    }
    specific = {
        "quality-report": {
            "datasets",
            "relationships",
            "parsing_errors",
            "conditional_missingness",
            "response_representations",
            "consistency_checks",
        },
        "kpis-summary": {"kpis", "granularity_analysis", "descriptive_statistics"},
    }
    if contract not in specific:
        raise ValueError(f"Contrato desconhecido: {contract}")
    missing = sorted((common | specific[contract]) - payload.keys())
    if missing:
        raise ValueError(
            f"Contrato {contract} incompleto: {', '.join(missing)}"
        )
    if payload["schema_version"] != "2.0":
        raise ValueError(f"Versão incompatível do contrato {contract}.")
    fingerprint = payload["source_fingerprint_sha256"]
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError(f"Fingerprint inválido no contrato {contract}.")
    # A serialização estrita também elimina NaN e Infinity antes do staging.
    json.dumps(_json_safe(payload), allow_nan=False)


def _split_reference(reference: str) -> tuple[str, str]:
    dataset_name, column = reference.split(".", 1)
    return dataset_name, column


def _source_manifest(
    source_dir: str | Path,
    datasets: dict[str, pd.DataFrame],
    *,
    snapshot_date: str | None = None,
) -> dict:
    """Descreve a remessa consumida sem publicar caminho nem conteúdo bruto."""
    source_path = Path(source_dir).expanduser()
    files = {}
    for dataset_name, filename in DATASET_FILES.items():
        content = (source_path / filename).read_bytes()
        files[dataset_name] = {
            "filename": filename,
            "size_bytes": len(content),
            "sha256": sha256(content).hexdigest(),
            "row_count": int(len(datasets[dataset_name])),
            "column_count": int(len(datasets[dataset_name].columns)),
        }
    return {
        "canonical_format": "csv-provisional",
        "authority_status": "pending_partner_confirmation",
        "snapshot_date": snapshot_date,
        "encoding": "utf-8-sig",
        "delimiter": ";",
        "null_policy": "apenas campos fisicamente vazios; texto não vazio é preservado",
        "files": files,
    }


def _normalized_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.casefold()


def _unique_mapping(
    frame: pd.DataFrame, *, key: str, value: str
) -> tuple[pd.Series, int]:
    """Cria mapa somente com chaves inequívocas e contabiliza duplicatas."""
    duplicated = frame[key].notna() & frame.duplicated(subset=[key], keep=False)
    unique = frame.loc[frame[key].notna() & ~duplicated, [key, value]]
    return unique.set_index(key)[value], int(duplicated.sum())


def _cross_consistency_checks(datasets: dict[str, pd.DataFrame]) -> list[dict]:
    """Quantifica inconsistências cruzadas sem expor valores identificadores."""
    pesquisas = datasets["pesquisas"]
    questoes = datasets["questoes"]
    clientes = datasets["clientes"]
    empresas = datasets["empresas"]
    respondentes = datasets["respondentes"]
    respostas = datasets["respostas"]

    research_titles, _ = _unique_mapping(
        pesquisas, key="id", value="titulo"
    )
    expected_titles = questoes["pesquisa_id"].map(research_titles)
    title_mismatch = (
        expected_titles.notna()
        & questoes["pesquisa_titulo"].notna()
        & _normalized_text(expected_titles).ne(
            _normalized_text(questoes["pesquisa_titulo"])
        )
    )

    client_companies, _ = _unique_mapping(
        clientes, key="id_cliente", value="id_empresa"
    )
    expected_companies = respondentes["id_cliente"].map(client_companies)
    company_mismatch = (
        expected_companies.notna()
        & respondentes["id_empresa"].notna()
        & expected_companies.ne(respondentes["id_empresa"])
    )
    mismatched_researches = int(
        respondentes.loc[company_mismatch, "id_pesq"].dropna().nunique()
    )

    valid_research_ids = set(pesquisas["id"].dropna())
    valid_participations = respondentes.loc[
        respondentes["id_pesq"].isin(valid_research_ids)
        & respondentes["id_pesq"].notna()
    ]
    observed = valid_participations.groupby("id_pesq").size()
    observed_by_research = pesquisas["id"].map(observed).fillna(0).astype("int64")
    declared = pd.to_numeric(pesquisas["participantes"], errors="coerce")
    comparable = declared.notna()
    declared_mismatch = comparable & declared.ne(observed_by_research)
    declared_excess = (
        declared.loc[comparable] - observed_by_research.loc[comparable]
    ).clip(lower=0)
    declared_without_observed = comparable & declared.gt(0) & observed_by_research.eq(0)

    participation_pairs = valid_participations[
        ["id_pesq", "id_empresa"]
    ].dropna().drop_duplicates()
    response_pairs = respostas[["pesquisa_id", "id_empresa"]].dropna()
    response_pair_check = response_pairs.merge(
        participation_pairs,
        how="left",
        left_on=["pesquisa_id", "id_empresa"],
        right_on=["id_pesq", "id_empresa"],
        indicator=True,
    )
    responses_without_pair = int(response_pair_check["_merge"].eq("left_only").sum())

    company_market, _ = _unique_mapping(
        empresas, key="ID", value="% de mercado"
    )
    current_market = respondentes["id_empresa"].map(company_market)
    respondent_market = pd.to_numeric(respondentes["market_share"], errors="coerce")
    market_comparable = current_market.notna() & respondent_market.notna()
    same_market = pd.Series(
        np.isclose(
            current_market.fillna(0).astype(float),
            respondent_market.fillna(0).astype(float),
            rtol=0.0,
            atol=1e-9,
        ),
        index=respondentes.index,
    )
    market_mismatch = market_comparable & ~same_market

    return [
        {
            "id": "titulo_questao_diverge_pesquisa",
            "severity": "warning",
            "description": "Título denormalizado da questão diverge do cadastro pai.",
            "affected_row_count": int(title_mismatch.sum()),
        },
        {
            "id": "empresa_participacao_diverge_contato",
            "severity": "ambiguity",
            "description": "Empresa registrada na participação diverge da empresa do contato.",
            "affected_row_count": int(company_mismatch.sum()),
            "affected_research_count": mismatched_researches,
        },
        {
            "id": "participantes_declarados_divergem_observados",
            "severity": "ambiguity",
            "description": "Quantidade declarada na pesquisa diverge das participações observadas.",
            "affected_row_count": int(declared_mismatch.sum()),
            "comparable_row_count": int(comparable.sum()),
            "declared_excess_total": int(declared_excess.sum()),
        },
        {
            "id": "participantes_declarados_sem_observacao",
            "severity": "ambiguity",
            "description": "Pesquisa declara participantes, mas não possui participação observada.",
            "affected_row_count": int(declared_without_observed.sum()),
        },
        {
            "id": "resposta_sem_par_participacao",
            "severity": "ambiguity",
            "description": "Par pesquisa/empresa da resposta não aparece nas participações; não há chave individual comum para concluir erro.",
            "affected_row_count": responses_without_pair,
        },
        {
            "id": "market_share_historico_diverge_cadastro_atual",
            "severity": "ambiguity",
            "description": "Market share da participação diverge do cadastro atual e pode representar snapshot histórico.",
            "affected_row_count": int(market_mismatch.sum()),
            "comparable_row_count": int(market_comparable.sum()),
        },
    ]


def _quality_report(
    datasets: dict[str, pd.DataFrame], parsing_errors: list[dict]
) -> dict:
    dataset_results = {
        name: audit_dataset(frame, name, primary_key=PRIMARY_KEYS[name])
        for name, frame in datasets.items()
    }
    relationship_results = []
    for relationship in RELATIONSHIPS:
        child_name, child_key = _split_reference(relationship["child"])
        parent_name, parent_key = _split_reference(relationship["parent"])
        relationship_results.append(
            audit_relationship(
                datasets[parent_name],
                datasets[child_name],
                parent_key=parent_key,
                child_key=child_key,
                parent_name=parent_name,
                child_name=child_name,
            )
        )

    questions = datasets["questoes"]
    question_types = questions["tipo"].astype("string").str.casefold()
    conditional = {
        "questoes.alternativas": audit_conditional_missingness(
            questions,
            column="alternativas",
            applicability_mask=question_types.isin(
                ["multipla_escolha", "caixas_de_selecao"]
            ),
        ),
        "questoes.linhas_matriz": audit_conditional_missingness(
            questions,
            column="linhas_matriz",
            applicability_mask=question_types.eq("matriz_avaliacao"),
        ),
        "questoes.colunas_matriz": audit_conditional_missingness(
            questions,
            column="colunas_matriz",
            applicability_mask=question_types.eq("matriz_avaliacao"),
        ),
    }

    responses = datasets["respostas"]
    _, duplicate_question_rows = _unique_mapping(
        questions, key="id_pergunta", value="tipo"
    )
    response_representations = audit_response_representations(responses, questions)

    pesquisas = datasets["pesquisas"]
    chronology_checks = {
        "entrega_antes_da_solicitacao": (
            pesquisas["data_entrega"].notna()
            & pesquisas["data_solicitacao"].notna()
            & pesquisas["data_entrega"].lt(pesquisas["data_solicitacao"])
        ),
        "divulgacao_antes_da_solicitacao": (
            pesquisas["data_divulgacao"].notna()
            & pesquisas["data_solicitacao"].notna()
            & pesquisas["data_divulgacao"].lt(pesquisas["data_solicitacao"])
        ),
        "limite_antes_da_divulgacao": (
            pesquisas["data_limite"].notna()
            & pesquisas["data_divulgacao"].notna()
            & pesquisas["data_limite"].lt(pesquisas["data_divulgacao"])
        ),
    }
    associado = datasets["empresas"]["Associado"].astype("string").str.strip()
    consistency_checks = [
        *(
            {
                "id": check_id,
                "severity": "warning",
                "description": "Ordem cronológica potencialmente inconsistente.",
                "affected_row_count": int(mask.sum()),
            }
            for check_id, mask in chronology_checks.items()
        ),
        {
            "id": "prazo_de_entrega_negativo",
            "severity": "error",
            "description": "Prazo calculado inferior a zero.",
            "affected_row_count": int(
                pesquisas["dias_uteis_para_entrega"].lt(0).sum()
            ),
        },
        {
            "id": "id_cliente_sentinela_si",
            "severity": "warning",
            "description": "Identificador usa o sentinela textual s/i.",
            "affected_row_count": int(
                datasets["clientes"]["id_cliente"].str.casefold().eq("s/i").sum()
            ),
        },
        {
            "id": "associado_variacao_caixa_sim",
            "severity": "warning",
            "description": "Valor equivalente a Sim usa variação de maiúsculas/minúsculas.",
            "affected_row_count": int(
                (associado.str.casefold().eq("sim") & associado.ne("Sim")).sum()
            ),
        },
        {
            "id": "questoes_id_pergunta_duplicado",
            "severity": "error",
            "description": "Chave de questão duplicada; o tipo é tratado como ambíguo nas respostas relacionadas.",
            "affected_row_count": duplicate_question_rows,
        },
        *_cross_consistency_checks(datasets),
    ]
    return {
        "datasets": dataset_results,
        "relationships": relationship_results,
        "parsing_errors": parsing_errors,
        "conditional_missingness": conditional,
        "response_representations": response_representations,
        "consistency_checks": consistency_checks,
    }


def _descriptive_statistics(datasets: dict[str, pd.DataFrame]) -> dict:
    numeric_variables = {
        "pesquisas.participantes": datasets["pesquisas"]["participantes"],
        "pesquisas.tempo_preenchimento": datasets["pesquisas"][
            "tempo_preenchimento"
        ],
        "pesquisas.dias_uteis_para_entrega": datasets["pesquisas"][
            "dias_uteis_para_entrega"
        ],
        "pesquisas.dias_uteis_aberta": datasets["pesquisas"]["dias úteis aberta"],
        "pesquisas.dias_para_tabulacao": datasets["pesquisas"][
            "dias para tabulação"
        ],
        "empresas.percentual_mercado": datasets["empresas"]["% de mercado"],
    }
    categorical_variables = {
        "pesquisas.status": datasets["pesquisas"]["status"],
        "pesquisas.tipo": datasets["pesquisas"]["tipo"],
        "pesquisas.complexidade": datasets["pesquisas"]["complexidade"],
        "empresas.Associado": datasets["empresas"]["Associado"],
        "clientes.departamento": datasets["clientes"]["departamento"],
        "questoes.tipo": datasets["questoes"]["tipo"],
    }
    numeric = {}
    for name, series in numeric_variables.items():
        outliers = detect_iqr_outliers(series)
        outliers.pop("outlier_values", None)
        numeric[name] = {
            "summary": describe_numeric(series),
            "iqr_outliers": outliers,
        }

    return {
        "numeric": numeric,
        "categorical": {
            name: describe_categorical(series)
            for name, series in categorical_variables.items()
        },
        "temporal": {
            "pesquisas.data_solicitacao": describe_temporal(
                datasets["pesquisas"]["data_solicitacao"], frequency="month"
            )
        },
    }


def _publish_transaction(files: list[tuple[Path, Path]], staging_root: Path) -> None:
    backup_root = staging_root / "backups"
    backups: list[tuple[Path, Path]] = []
    published: list[Path] = []
    try:
        for _, target in files:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                backup = backup_root / str(len(backups))
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, backup)
                backups.append((backup, target))
        for staged, target in files:
            os.replace(staged, target)
            published.append(target)
    except Exception:
        for target in reversed(published):
            target.unlink(missing_ok=True)
        for backup, target in reversed(backups):
            os.replace(backup, target)
        raise


def run_analysis(
    source_dir: str | Path,
    output_dir: str | Path,
    *,
    generated_at: datetime | None = None,
    charts_dir: str | Path | None = None,
    snapshot_date: str | None = None,
) -> dict[str, Any]:
    """Executa o pipeline completo sem sobrescrever as fontes recebidas."""
    if snapshot_date is not None:
        try:
            datetime.strptime(snapshot_date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("snapshot_date deve usar o formato AAAA-MM-DD.") from exc
    datasets = load_datasets(source_dir)
    normalized, parsing_errors = normalize_datasets(datasets)
    timestamp = _generated_at(generated_at)
    fingerprint = source_fingerprint(source_dir)
    source_manifest = _source_manifest(
        source_dir, normalized, snapshot_date=snapshot_date
    )

    quality_results = _quality_report(normalized, parsing_errors)
    quality = {
        "schema_version": "2.0",
        "contract_schema": "schemas/quality-report-v2.schema.json",
        "generated_at": timestamp,
        "source_fingerprint_sha256": fingerprint,
        "source_manifest": source_manifest,
        **quality_results,
    }
    kpis = {
        "schema_version": "2.0",
        "contract_schema": "schemas/kpis-summary-v2.schema.json",
        "generated_at": timestamp,
        "source_fingerprint_sha256": fingerprint,
        "source_manifest": source_manifest,
        "kpis": calculate_kpis(normalized),
        "granularity_analysis": compare_granularities(normalized),
        "descriptive_statistics": _descriptive_statistics(normalized),
    }
    _validate_output_contract(quality, "quality-report")
    _validate_output_contract(kpis, "kpis-summary")

    output_path = Path(output_dir)
    charts_path = Path(charts_dir) if charts_dir is not None else output_path / "charts"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    charts_path.parent.mkdir(parents=True, exist_ok=True)
    if os.stat(output_path.parent).st_dev != os.stat(charts_path.parent).st_dev:
        raise ValueError("JSON e gráficos devem ser publicados no mesmo volume.")
    with tempfile.TemporaryDirectory(
        prefix=".g02-analysis-", dir=output_path.parent
    ) as temporary:
        staging_root = Path(temporary)
        staging_json = staging_root / "json"
        staging_charts = staging_root / "charts"
        staging_json.mkdir()
        quality_staged = staging_json / "quality_report.json"
        kpis_staged = staging_json / "kpis_summary.json"
        _write_json(quality_staged, quality)
        _write_json(kpis_staged, kpis)
        chart_staged = generate_charts(normalized, quality, staging_charts)

        quality_target = output_path / quality_staged.name
        kpis_target = output_path / kpis_staged.name
        chart_targets = [charts_path / chart.name for chart in chart_staged]
        files = [
            (quality_staged, quality_target),
            (kpis_staged, kpis_target),
            *zip(chart_staged, chart_targets, strict=True),
        ]
        _publish_transaction(list(files), staging_root)

    return {
        "quality_report": quality_target,
        "kpis_summary": kpis_target,
        "charts": chart_targets,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa a modelagem quantitativa das seis bases do parceiro."
    )
    parser.add_argument(
        "--snapshot-date",
        default=os.getenv("PARTNER_SNAPSHOT_DATE"),
        help="Data de recebimento/corte da remessa, no formato AAAA-MM-DD.",
    )
    parser.add_argument(
        "--source-dir",
        default=os.getenv("PARTNER_DATA_DIR"),
        help="Diretório dos seis CSVs; alternativa: variável PARTNER_DATA_DIR.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "data",
        help="Diretório dos contratos JSON.",
    )
    parser.add_argument(
        "--charts-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "images",
        help="Diretório dos gráficos PNG agregados.",
    )
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    if not args.source_dir:
        parser.error("Informe --source-dir ou defina PARTNER_DATA_DIR.")
    result = run_analysis(
        args.source_dir,
        args.output_dir,
        charts_dir=args.charts_dir,
        snapshot_date=args.snapshot_date,
    )
    print(
        f"Pipeline concluído: 2 contratos JSON e {len(result['charts'])} gráficos."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
