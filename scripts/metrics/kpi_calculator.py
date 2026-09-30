"""Seis indicadores auditáveis e comparações de granularidade do Artefato 3."""

from __future__ import annotations

from typing import Any

import pandas as pd

from scripts.data_quality.schema import CRITICAL_FIELDS


def _percentage(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    if denominator < 0 or numerator < 0:
        raise ValueError("Numerador e denominador de percentuais não podem ser negativos.")
    value = float(numerator / denominator * 100)
    if value < -1e-9 or value > 100 + 1e-9:
        raise ValueError("Percentuais devem compartilhar um universo e permanecer entre 0 e 100.")
    return min(100.0, max(0.0, value))


def _id_counts(series: pd.Series) -> dict[str, int]:
    counts = series.dropna().astype("string").value_counts()
    return {str(key): int(counts[key]) for key in sorted(counts.index.astype(str))}


def _research_ids(pesquisas: pd.DataFrame) -> list[str]:
    return sorted(pesquisas["id"].dropna().astype("string").unique().tolist())


def _counts_by_research(
    pesquisas: pd.DataFrame, participations: pd.DataFrame
) -> dict[str, int]:
    """Materializa toda pesquisa cadastrada, inclusive as sem participação."""
    counts = _id_counts(participations["id_pesq"])
    return {research_id: counts.get(research_id, 0) for research_id in _research_ids(pesquisas)}


def _summary(values: Any) -> dict[str, float | int | None]:
    """Resume uma coleção numérica sem esconder zeros materializados."""
    if isinstance(values, dict):
        values = list(values.values())
    numeric = pd.to_numeric(pd.Series(values, dtype="object"), errors="coerce").dropna()
    if numeric.empty:
        return {
            "observation_count": 0,
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
        }
    return {
        "observation_count": int(len(numeric)),
        "mean": float(numeric.mean()),
        "median": float(numeric.median()),
        "minimum": float(numeric.min()),
        "maximum": float(numeric.max()),
    }


def _kpi(
    *,
    identifier: str,
    name: str,
    objective: str,
    formula: str,
    variables: list[str],
    granularity: str,
    filters: list[str],
    numerator: Any,
    denominator: Any,
    value: Any,
    unit: str,
    valid_observations: int,
    expected_observations: int,
    interpretation: str,
    limitations: list[str],
    coverage_unit: str = "observações",
    indicator_status: str = "descriptive",
    population_definition: str = "",
    zero_materialized_count: int = 0,
    summary: dict[str, Any] | None = None,
    assumptions: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict:
    coverage = _percentage(valid_observations, expected_observations)
    result = {
        "id": identifier,
        "name": name,
        "objective": objective,
        "formula": formula,
        "variables": variables,
        "granularity": granularity,
        "filters": filters,
        "numerator": numerator,
        "denominator": denominator,
        "value": value,
        "unit": unit,
        "valid_observations": valid_observations,
        "expected_observations": expected_observations,
        "coverage_pct": coverage,
        "coverage_unit": coverage_unit,
        "definition_version": "2.0",
        "indicator_status": indicator_status,
        "population_definition": population_definition,
        "excluded_observations": max(expected_observations - valid_observations, 0),
        "zero_materialized_count": zero_materialized_count,
        "summary": summary,
        "assumptions": assumptions or [],
        "interpretation": interpretation,
        "limitations": limitations,
    }
    if extra:
        result.update(extra)
    return result


def _valid_participations(
    empresas: pd.DataFrame,
    pesquisas: pd.DataFrame,
    respondentes: pd.DataFrame,
) -> pd.DataFrame:
    """Mantém participações cujas pesquisa e empresa existem nas tabelas-mãe."""
    valid_research_ids = set(pesquisas["id"].dropna().astype("string"))
    valid_company_ids = set(empresas["ID"].dropna().astype("string"))
    mask = (
        respondentes["id_pesq"].notna()
        & respondentes["id_empresa"].notna()
        & respondentes["id_pesq"].astype("string").isin(valid_research_ids)
        & respondentes["id_empresa"].astype("string").isin(valid_company_ids)
    )
    return respondentes.loc[mask].copy()


def _company_coverage(
    empresas: pd.DataFrame,
    pesquisas: pd.DataFrame,
    respondentes: pd.DataFrame,
) -> tuple[dict[str, float] | None, dict[str, int], int]:
    company_ids = set(empresas["ID"].dropna().astype("string"))
    denominator = len(company_ids)
    registered_participations = _valid_participations(
        empresas, pesquisas, respondentes
    )
    pairs = registered_participations[
        ["id_pesq", "id_empresa"]
    ].drop_duplicates()
    numerators = _counts_by_research(pesquisas, pairs)
    if denominator == 0:
        return None, numerators, denominator
    values = {
        key: _percentage(numerator, denominator)
        for key, numerator in numerators.items()
    }
    return values, numerators, denominator


def _critical_missingness_scorecards(
    datasets: dict[str, pd.DataFrame],
) -> tuple[int, int, dict[str, dict]]:
    """Calcula micro média e diagnósticos sem misturar campos ou grãos."""
    grain_names = {
        "pesquisas": "pesquisa",
        "empresas": "empresa",
        "respondentes": "participação",
    }
    by_field: dict[str, dict] = {}
    fields_by_dataset: dict[str, list[str]] = {}
    missing_total = 0
    expected_total = 0

    for reference in CRITICAL_FIELDS:
        dataset_name, column = reference.split(".", 1)
        series = datasets[dataset_name][column]
        missing = int(series.isna().sum())
        expected = len(series)
        missing_total += missing
        expected_total += expected
        fields_by_dataset.setdefault(dataset_name, []).append(column)
        by_field[reference] = {
            "dataset": dataset_name,
            "field": column,
            "grain": grain_names[dataset_name],
            "missing_cells": missing,
            "expected_cells": expected,
            "missing_pct": _percentage(missing, expected),
            "completeness_pct": _percentage(expected - missing, expected),
        }

    by_grain: dict[str, dict] = {}
    for dataset_name, columns in fields_by_dataset.items():
        frame = datasets[dataset_name]
        missing_mask = frame[columns].isna()
        missing_cells = int(missing_mask.sum().sum())
        expected_cells = int(len(frame) * len(columns))
        affected_entities = int(missing_mask.any(axis=1).sum())
        by_grain[grain_names[dataset_name]] = {
            "dataset": dataset_name,
            "fields": [f"{dataset_name}.{column}" for column in columns],
            "missing_cells": missing_cells,
            "expected_cells": expected_cells,
            "missing_pct": _percentage(missing_cells, expected_cells),
            "affected_entities": affected_entities,
            "total_entities": len(frame),
            "affected_entities_pct": _percentage(affected_entities, len(frame)),
        }

    return missing_total, expected_total, {
        "by_field": by_field,
        "by_grain": by_grain,
    }


def calculate_kpis(datasets: dict[str, pd.DataFrame]) -> list[dict]:
    """Calcula somente os seis indicadores mínimos definidos na SPEC."""
    empresas = datasets["empresas"]
    pesquisas = datasets["pesquisas"]
    respondentes = datasets["respondentes"]
    respostas = datasets["respostas"]

    valid_dates = pesquisas["data_solicitacao"].dropna()
    volume_by_month = {
        str(period): int(count)
        for period, count in (
            valid_dates.dt.to_period("M").astype("string").value_counts().sort_index()
        ).items()
    }

    statuses = pesquisas["status"].dropna().astype("string").str.strip()
    statuses = statuses[statuses.ne("")]
    status_counts = statuses.value_counts().sort_index()
    status_denominator = len(statuses)
    status_percentages = {
        str(status): float(count / status_denominator * 100)
        for status, count in status_counts.items()
    }

    company_coverage, coverage_numerators, company_denominator = _company_coverage(
        empresas, pesquisas, respondentes
    )

    delivery = pd.to_numeric(
        pesquisas["dias_uteis_para_entrega"], errors="coerce"
    )
    valid_delivery = delivery[delivery.notna() & delivery.ge(0)]
    final_status = (
        pesquisas["status"]
        .astype("string")
        .str.strip()
        .str.casefold()
        .isin(["finalizada", "finalizado", "concluída", "concluida"])
    )
    final_delivery = delivery[final_status & delivery.notna() & delivery.ge(0)]

    valid_participations = _valid_participations(empresas, pesquisas, respondentes)
    participation_counts = _counts_by_research(pesquisas, valid_participations)

    registered_participations = valid_participations

    missing_critical, expected_critical, critical_scorecards = (
        _critical_missingness_scorecards(datasets)
    )
    missing_pct = _percentage(missing_critical, expected_critical)

    return [
        _kpi(
            identifier="KPI-01",
            name="Volume de pesquisas por período",
            objective="Acompanhar a demanda de pesquisas ao longo do tempo.",
            formula="COUNT(pesquisas.id) por mês de data_solicitacao válida",
            variables=["pesquisas.id", "pesquisas.data_solicitacao"],
            granularity="mês",
            filters=["data_solicitacao válida"],
            numerator=len(valid_dates),
            denominator=None,
            value=volume_by_month,
            unit="pesquisas",
            valid_observations=len(valid_dates),
            expected_observations=len(pesquisas),
            interpretation="Cada valor representa pesquisas solicitadas no mês.",
            limitations=["Pesquisas sem data válida não entram na distribuição."],
            population_definition="Pesquisas com data_solicitacao válida, agregadas por mês.",
            summary=_summary(volume_by_month),
        ),
        _kpi(
            identifier="KPI-02",
            name="Percentual de pesquisas por status",
            objective="Descrever a composição operacional do portfólio de pesquisas.",
            formula="COUNT(status = s) / COUNT(status preenchido) × 100",
            variables=["pesquisas.status"],
            granularity="pesquisa",
            filters=["status preenchido"],
            numerator={str(key): int(value) for key, value in status_counts.items()},
            denominator=status_denominator,
            value=status_percentages,
            unit="percentual",
            valid_observations=status_denominator,
            expected_observations=len(pesquisas),
            interpretation="Os percentuais mostram a participação de cada status válido.",
            limitations=["As categorias de status não têm ordem matemática presumida."],
            population_definition="Pesquisas com status preenchido.",
            summary=_summary(status_percentages),
        ),
        _kpi(
            identifier="KPI-03",
            name="Cobertura de empresas cadastradas por pesquisa",
            objective="Medir a cobertura observada sobre o cadastro de empresas em cada pesquisa.",
            formula="Empresas cadastradas distintas com participação / empresas cadastradas × 100",
            variables=[
                "respondentes.id_pesq",
                "respondentes.id_empresa",
                "empresas.ID",
            ],
            granularity="pesquisa",
            filters=[
                "pesquisa existente no cadastro",
                "id_empresa preenchido e existente no cadastro",
                "pares pesquisa/empresa distintos",
                "todas as pesquisas cadastradas, inclusive com zero participação",
            ],
            numerator=coverage_numerators,
            denominator=company_denominator,
            value=company_coverage,
            unit="percentual",
            valid_observations=len(registered_participations),
            expected_observations=len(respondentes),
            coverage_unit="linhas de participação",
            interpretation=(
                "Percentual do cadastro total de empresas observado em cada pesquisa; "
                "zero representa pesquisa cadastrada sem participação válida."
            ),
            limitations=[
                "Todas as empresas cadastradas são usadas como aproximação do universo elegível.",
                "A elegibilidade por pesquisa não foi fornecida pelo parceiro.",
                "Este indicador é cobertura sobre cadastro, não taxa oficial de adesão.",
                "Participações ligadas a pesquisas ou empresas ausentes do cadastro são excluídas.",
            ],
            population_definition=(
                "Todas as pesquisas e empresas cadastradas; empresas observadas são "
                "distintas dentro de cada pesquisa."
            ),
            zero_materialized_count=sum(
                value == 0 for value in coverage_numerators.values()
            ),
            summary=_summary(company_coverage or []),
            assumptions=[
                "O cadastro completo substitui provisoriamente a população elegível não fornecida."
            ],
        ),
        _kpi(
            identifier="KPI-04",
            name="Proxy de tempo médio de entrega pelo campo pré-calculado",
            objective="Descrever o prazo médio disponível no campo pré-calculado da fonte.",
            formula="SUM(dias válidos não negativos) / COUNT(dias válidos não negativos)",
            variables=["pesquisas.dias_uteis_para_entrega"],
            granularity="pesquisa",
            filters=["dias_uteis_para_entrega >= 0"],
            numerator=float(valid_delivery.sum()) if len(valid_delivery) else 0.0,
            denominator=len(valid_delivery),
            value=float(valid_delivery.mean()) if len(valid_delivery) else None,
            unit="dias úteis",
            valid_observations=len(valid_delivery),
            expected_observations=len(pesquisas),
            interpretation=(
                "Proxy calculado somente sobre valores preenchidos, não negativos e já "
                "pré-calculados na fonte."
            ),
            limitations=[
                (
                    "Não representa oficialmente o intervalo solicitação-publicação até que "
                    "o parceiro defina campos, status e calendário."
                ),
                "A média não representa pesquisas sem prazo calculável.",
            ],
            indicator_status="proxy",
            population_definition=(
                "Pesquisas com dias_uteis_para_entrega preenchido e não negativo."
            ),
            summary=_summary(valid_delivery),
            assumptions=[
                "O campo pré-calculado é usado sem afirmar que representa publicação oficial."
            ],
            extra={
                "sensitivity_analysis": {
                    "completed_researches_only": {
                        "valid_observations": int(len(final_delivery)),
                        "mean_days": (
                            float(final_delivery.mean())
                            if len(final_delivery)
                            else None
                        ),
                    }
                }
            },
        ),
        _kpi(
            identifier="KPI-05",
            name="Participações registradas por pesquisa",
            objective="Medir o volume de participações observado em cada pesquisa.",
            formula="COUNT(linhas com id_pesq e id_empresa preenchidos) por pesquisa cadastrada",
            variables=["respondentes.id_pesq", "respondentes.id_empresa"],
            granularity="pesquisa",
            filters=[
                "id_pesq preenchido e existente no cadastro de pesquisas",
                "id_empresa preenchido e existente no cadastro de empresas",
                "todas as pesquisas cadastradas, inclusive com zero participação",
            ],
            numerator=len(valid_participations),
            denominator=None,
            value=participation_counts,
            unit="participações",
            valid_observations=len(valid_participations),
            expected_observations=len(respondentes),
            coverage_unit="linhas de participação",
            interpretation=(
                "Cada linha válida representa uma participação registrada; zero representa "
                "pesquisa cadastrada sem participação válida."
            ),
            limitations=[
                "Não é uma taxa: não existe denominador confiável de convidados.",
                "respondent_id não é usado para inferir ligação individual.",
                "Participações ligadas a pesquisas ou empresas ausentes são excluídas.",
            ],
            population_definition=(
                "Todas as pesquisas cadastradas; contagem de linhas com pesquisa e empresa válidas."
            ),
            zero_materialized_count=sum(
                value == 0 for value in participation_counts.values()
            ),
            summary=_summary(participation_counts),
        ),
        _kpi(
            identifier="KPI-06",
            name="Micro média de ausência em campos críticos",
            objective=(
                "Quantificar células ausentes no conjunto crítico e revelar sua distribuição "
                "por campo e unidade de análise."
            ),
            formula=(
                "Soma das células críticas ausentes / soma das células críticas "
                "esperadas × 100"
            ),
            variables=list(CRITICAL_FIELDS),
            granularity="célula (micro), campo e unidade de análise",
            filters=[f"lista explícita de {len(CRITICAL_FIELDS)} campos críticos"],
            numerator=missing_critical,
            denominator=expected_critical,
            value=missing_pct,
            unit="percentual",
            valid_observations=expected_critical - missing_critical,
            expected_observations=expected_critical,
            coverage_unit="células críticas",
            interpretation=(
                "Micro média ponderada pelo número de células; os scorecards mostram campos "
                "e grãos sem mascará-los pelo tamanho das bases."
            ),
            limitations=[
                "O resultado depende da lista de campos críticos declarada na SPEC.",
                (
                    "A micro média não deve ser interpretada isoladamente porque bases "
                    "maiores têm maior peso."
                ),
            ],
            indicator_status="diagnostic",
            population_definition="Células dos sete campos críticos declarados na SPEC.",
            summary=_summary([missing_pct] if missing_pct is not None else []),
            extra={"scorecards": critical_scorecards},
        ),
    ]


def compare_granularities(datasets: dict[str, pd.DataFrame]) -> list[dict]:
    """Compara cobertura e participações em grãos que mudam a interpretação."""
    empresas = datasets["empresas"]
    pesquisas = datasets["pesquisas"]
    respondentes = datasets["respondentes"]
    coverage_by_research, _, company_denominator = _company_coverage(
        empresas, pesquisas, respondentes
    )
    valid_participations = _valid_participations(empresas, pesquisas, respondentes)
    registered_participations = valid_participations
    participant_companies = registered_participations["id_empresa"].nunique()
    global_coverage = _percentage(participant_companies, company_denominator)

    participation_by_research = _counts_by_research(pesquisas, valid_participations)
    participation_by_company = _id_counts(valid_participations["id_empresa"])
    return [
        {
            "indicator_id": "KPI-03",
            "values_by_granularity": {
                "global": global_coverage,
                "pesquisa": coverage_by_research,
            },
            "denominator_note": (
                "A cobertura usa somente empresas existentes no mesmo cadastro do denominador. "
                "O grão global conta cada empresa uma vez; por pesquisa, a mesma empresa pode "
                "participar em vários instrumentos, e pesquisas sem participação recebem zero."
            ),
            "weighting_note": (
                "A média simples das pesquisas não equivale necessariamente à cobertura global."
            ),
        },
        {
            "indicator_id": "KPI-05",
            "values_by_granularity": {
                "global": len(valid_participations),
                "pesquisa": participation_by_research,
                "empresa": participation_by_company,
            },
            "denominator_note": (
                "São contagens de registros, sem população de convidados para formar uma taxa."
            ),
            "weighting_note": (
                "Pesquisas e empresas com mais registros exercem maior peso no total global."
            ),
        },
    ]
