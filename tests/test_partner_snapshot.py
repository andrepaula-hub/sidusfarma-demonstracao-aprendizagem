"""Regressão opcional da remessa real, ativada sem codificar caminho pessoal."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import pandas as pd


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("PARTNER_DATA_DIR"),
        reason="Defina PARTNER_DATA_DIR para validar a remessa real do parceiro.",
    ),
]


@pytest.fixture(scope="module")
def partner_data_dir() -> Path:
    configured = os.getenv("PARTNER_DATA_DIR")
    if not configured:
        pytest.skip("Defina PARTNER_DATA_DIR para validar a remessa real do parceiro.")
    path = Path(configured)
    if not path.is_dir():
        pytest.fail("PARTNER_DATA_DIR não aponta para um diretório existente.")
    return path


def test_partner_snapshot_reproduces_inventory_counts(ingestion_api, partner_data_dir):
    datasets = ingestion_api.load_datasets(partner_data_dir)
    assert {name: frame.shape for name, frame in datasets.items()} == {
        "clientes": (5430, 5),
        "empresas": (779, 9),
        "pesquisas": (366, 33),
        "questoes": (231, 13),
        "respondentes": (18735, 6),
        "respostas": (20607, 9),
    }


def test_partner_snapshot_reproduces_documented_orphans(
    ingestion_api, quality_api, partner_data_dir
):
    datasets = ingestion_api.load_datasets(partner_data_dir)
    normalized, _ = ingestion_api.normalize_datasets(datasets)

    questions = quality_api.audit_relationship(
        normalized["pesquisas"],
        normalized["questoes"],
        parent_key="id",
        child_key="pesquisa_id",
        parent_name="pesquisas",
        child_name="questoes",
    )
    participants = quality_api.audit_relationship(
        normalized["pesquisas"],
        normalized["respondentes"],
        parent_key="id",
        child_key="id_pesq",
        parent_name="pesquisas",
        child_name="respondentes",
    )
    answers = quality_api.audit_relationship(
        normalized["pesquisas"],
        normalized["respostas"],
        parent_key="id",
        child_key="pesquisa_id",
        parent_name="pesquisas",
        child_name="respostas",
    )

    assert (questions["orphan_value_count"], questions["orphan_row_count"]) == (4, 43)
    assert (participants["orphan_value_count"], participants["orphan_row_count"]) == (1, 55)
    assert (answers["orphan_value_count"], answers["orphan_row_count"]) == (4, 3592)


def test_partner_snapshot_reproduces_response_and_kpi_contracts(
    ingestion_api, quality_api, kpi_api, partner_data_dir
):
    datasets = ingestion_api.load_datasets(partner_data_dir)
    normalized, _ = ingestion_api.normalize_datasets(datasets)

    representations = quality_api.audit_response_representations(
        normalized["respostas"], normalized["questoes"]
    )
    assert representations["total_row_count"] == 20607
    assert representations["evaluable_row_count"] == 20607
    assert representations["valid_representation_count"] == 20607
    assert representations["missing_representation_count"] == 0
    assert representations["not_evaluable_row_count"] == 0
    assert representations["physical_missing_count_by_column"]["valor"] == 8307

    by_id = {
        item["id"]: item for item in kpi_api.calculate_kpis(normalized)
    }
    assert by_id["KPI-03"]["zero_materialized_count"] == 40
    assert by_id["KPI-03"]["summary"] == {
        "observation_count": 366,
        "mean": pytest.approx(6.548608626724749),
        "median": pytest.approx(6.675224646983312),
        "minimum": 0.0,
        "maximum": pytest.approx(24.005134788189987),
    }
    assert by_id["KPI-05"]["numerator"] == 18680
    assert by_id["KPI-05"]["expected_observations"] == 18735
    assert by_id["KPI-05"]["coverage_pct"] == pytest.approx(99.70643181211636)
    assert by_id["KPI-05"]["zero_materialized_count"] == 40
    assert by_id["KPI-05"]["summary"] == {
        "observation_count": 366,
        "mean": pytest.approx(51.03825136612022),
        "median": 52.0,
        "minimum": 0.0,
        "maximum": 187.0,
    }
    assert by_id["KPI-06"]["numerator"] == 39
    assert by_id["KPI-06"]["denominator"] == 39713
    assert by_id["KPI-06"]["scorecards"]["by_grain"]["pesquisa"][
        "affected_entities"
    ] == 35


def test_partner_snapshot_records_known_csv_xlsx_drift(partner_data_dir):
    """Impede que divergências recebidas sejam reconciliadas silenciosamente."""
    clientes_csv = pd.read_csv(
        partner_data_dir / "clientes.csv",
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=False,
    )
    clientes_xlsx = pd.read_excel(
        partner_data_dir / "clientes.xlsx",
        dtype="string",
        keep_default_na=False,
    )
    csv_clients = set(clientes_csv["id_cliente"].str.strip())
    xlsx_clients = set(clientes_xlsx["id_cliente"].str.strip())
    assert len(csv_clients - xlsx_clients) == 1
    assert len(xlsx_clients - csv_clients) == 0

    respostas_csv = pd.read_csv(
        partner_data_dir / "respostas.csv",
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=False,
    ).set_index("id_resposta")
    respostas_xlsx = pd.read_excel(
        partner_data_dir / "respostas.xlsx",
        dtype="string",
        keep_default_na=False,
    ).set_index("id_resposta")
    common_ids = respostas_csv.index.intersection(respostas_xlsx.index)
    csv_values = respostas_csv.loc[common_ids, "valor"].fillna("").str.strip()
    xlsx_values = respostas_xlsx.loc[common_ids, "valor"].fillna("").str.strip()
    assert int(csv_values.ne(xlsx_values).sum()) == 72
