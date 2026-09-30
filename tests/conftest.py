"""Fixtures sintéticas e carregamento dos contratos do pipeline quantitativo."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _require_callable(module_name: str, callable_name: str):
    """Pula contratos dependentes até o teste-guarda liberar o módulo."""
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if not (module_name == exc.name or module_name.startswith(f"{exc.name}.")):
            raise
        pytest.skip(
            f"Contrato TDD pendente: implemente o módulo {module_name!r} ({exc}).",
        )

    value = getattr(module, callable_name, None)
    if not callable(value):
        pytest.skip(
            f"Contrato TDD pendente: implemente {module_name}.{callable_name}().",
        )
    return value


@pytest.fixture(scope="session")
def ingestion_api():
    return SimpleNamespace(
        load_datasets=_require_callable(
            "scripts.data_quality.ingestion", "load_datasets"
        ),
        normalize_datasets=_require_callable(
            "scripts.data_quality.normalization", "normalize_datasets"
        ),
    )


@pytest.fixture(scope="session")
def quality_api():
    return SimpleNamespace(
        audit_dataset=_require_callable(
            "scripts.data_quality.audit", "audit_dataset"
        ),
        audit_relationship=_require_callable(
            "scripts.data_quality.audit", "audit_relationship"
        ),
        audit_conditional_missingness=_require_callable(
            "scripts.data_quality.audit", "audit_conditional_missingness"
        ),
        audit_response_representations=_require_callable(
            "scripts.data_quality.audit", "audit_response_representations"
        ),
    )


@pytest.fixture(scope="session")
def descriptive_api():
    return SimpleNamespace(
        describe_numeric=_require_callable(
            "scripts.metrics.descriptive", "describe_numeric"
        ),
        describe_categorical=_require_callable(
            "scripts.metrics.descriptive", "describe_categorical"
        ),
        describe_temporal=_require_callable(
            "scripts.metrics.descriptive", "describe_temporal"
        ),
        detect_iqr_outliers=_require_callable(
            "scripts.metrics.descriptive", "detect_iqr_outliers"
        ),
    )


@pytest.fixture(scope="session")
def kpi_api():
    return SimpleNamespace(
        calculate_kpis=_require_callable(
            "scripts.metrics.kpi_calculator", "calculate_kpis"
        ),
        compare_granularities=_require_callable(
            "scripts.metrics.kpi_calculator", "compare_granularities"
        ),
    )


@pytest.fixture(scope="session")
def runner_api():
    return SimpleNamespace(
        run_analysis=_require_callable(
            "scripts.runners.run_full_analysis", "run_analysis"
        ),
        publish_transaction=_require_callable(
            "scripts.runners.run_full_analysis", "_publish_transaction"
        ),
    )


@pytest.fixture
def synthetic_datasets() -> dict[str, pd.DataFrame]:
    """Seis bases pequenas, coerentes entre si e sem dados reais do parceiro."""
    return {
        "clientes": pd.DataFrame(
            {
                "id_cliente": ["c1", "c2", "c3", "s/i"],
                "id_empresa": ["1", "2", "3", None],
                "cargo": ["Analista", "Gerente", "Analista", None],
                "departamento": ["Dados", "RH", "Dados", None],
                "e-mail": [
                    "alpha@example.invalid",
                    "beta@example.invalid",
                    "gamma@example.invalid",
                    None,
                ],
            }
        ),
        "empresas": pd.DataFrame(
            {
                "ID": ["1", "2", "3", "4"],
                "Nome Fantasia": ["Empresa A", "Empresa B", "Empresa C", "Empresa D"],
                "% de mercado": ["10,00%", "20,00%", "30,00%", "40,00%"],
                "Nacionalidade": ["Nacional", "Nacional", "Estrangeira", "Nacional"],
                "Associado": ["Sim", "Sim", "Não", "Não"],
                "Tipo de Associado": ["Efetivo", "Efetivo", None, None],
                "Cidade": ["São Paulo", "Campinas", "Rio de Janeiro", "Curitiba"],
                "Estado": ["SP", "SP", "RJ", "PR"],
                "País": ["Brasil", "Brasil", "Brasil", "Brasil"],
            }
        ),
        "pesquisas": pd.DataFrame(
            {
                "id": ["10", "11", "12", "13"],
                "titulo": ["Pesquisa A", "Pesquisa B", "Pesquisa C", "Pesquisa D"],
                "status": ["Finalizada", "Em andamento", "Finalizada", "Cancelada"],
                "tipo": ["Anual", "Pontual", "Anual", "Pontual"],
                "area": ["Dados", "RH", "Dados", "Comercial"],
                "participantes": [2, 1, 1, None],
                "part_mercado": ["30,00%", "20,00%", "30,00%", None],
                "data_solicitacao": ["01/01/2024", "15/01/2024", "01/02/2024", "inválida"],
                "data_aprov": [None, None, None, None],
                "data_divulgacao": ["02/01/2024", "16/01/2024", "02/02/2024", None],
                "data_limite": ["10/01/2024", "30/01/2024", "10/02/2024", None],
                "prorrogada_ate": [None, None, "15/02/2024", None],
                "data_entrega": ["12/01/2024", None, "20/02/2024", None],
                "dias_uteis_para_entrega": [10, 20, -3, None],
                "complexidade": ["baixa", "média", "alta", None],
                "tipo de resposta": ["empresa", "empresa", "empresa", "empresa"],
                "tempo_preenchimento": [5, 10, None, None],
                "objetivos": ["A", "B", "C", "D"],
                "dia da semana de lançamento": [2, 3, 5, None],
                "dias úteis aberta": [7, 10, 7, None],
                "dias entre a solicitação e a divulgação": [1, 1, 1, None],
                "dias para tabulação": [2, 3, 4, None],
                **{f"Unnamed: {index}": [None] * 4 for index in range(22, 33)},
            }
        ),
        "questoes": pd.DataFrame(
            {
                "id_pergunta": ["100", "101", "102"],
                "pesquisa_id": ["10", "10", "12"],
                "pesquisa_titulo": ["Pesquisa A", "Pesquisa A", "Pesquisa C"],
                "enunciado": ["Pergunta A", "Pergunta B", "Pergunta C"],
                "tipo": ["multipla_escolha", "aberta", "numerica"],
                "qtd_alternativas": [2, None, None],
                "alternativas": ["Sim | Não", None, None],
                "linhas_matriz": [None, None, None],
                "colunas_matriz": [None, None, None],
                "confianca": ["alta", "alta", "média"],
                "formato_arquivo": ["new", "new", "new"],
                "col_origem": ["20", "21", "22"],
                "observacoes": [None, None, None],
            }
        ),
        "respondentes": pd.DataFrame(
            {
                "id_pesq": ["10", "10", "11", "12"],
                "hora_inicio": ["01/01/2024 10:00", "01/01/2024 11:00", None, None],
                "hora_termino": ["01/01/2024 10:05", "01/01/2024 11:08", None, None],
                "id_empresa": ["1", "2", "2", "3"],
                "market_share": ["10,00%", "20,00%", "20,00%", "30,00%"],
                "id_cliente": ["c1", "c2", "c2", "c3"],
            }
        ),
        "respostas": pd.DataFrame(
            {
                "id_resposta": ["1000", "1001", "1002", "1003"],
                "pesquisa_id": ["10", "10", "10", "12"],
                "id_pergunta": ["100", "100", "101", "102"],
                "respondent_id": ["r-a", "r-b", "r-a", "r-c"],
                "id_empresa": ["1", "2", "1", "3"],
                "alternativa": ["Sim", "Não", None, None],
                "linha_matriz": [None, None, None, None],
                "coluna_matriz": [None, None, None, None],
                "valor": [None, None, "texto sintético", "42"],
            }
        ),
    }


@pytest.fixture
def synthetic_source_dir(tmp_path: Path, synthetic_datasets) -> Path:
    source_dir = tmp_path / "partner-data"
    source_dir.mkdir()
    for name, frame in synthetic_datasets.items():
        frame.to_csv(
            source_dir / f"{name}.csv",
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )
    return source_dir
