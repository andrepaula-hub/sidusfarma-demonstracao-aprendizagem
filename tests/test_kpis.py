"""Contratos dos indicadores mínimos do Artefato 3."""

from __future__ import annotations

import pytest


MANDATORY_FIELDS = {
    "id",
    "name",
    "objective",
    "formula",
    "variables",
    "granularity",
    "filters",
    "numerator",
    "denominator",
    "value",
    "unit",
    "valid_observations",
    "expected_observations",
    "coverage_pct",
    "coverage_unit",
    "interpretation",
    "limitations",
}


@pytest.fixture
def calculated_kpis(ingestion_api, kpi_api, synthetic_datasets):
    normalized, _ = ingestion_api.normalize_datasets(synthetic_datasets)
    return kpi_api.calculate_kpis(normalized)


def _by_id(kpis):
    return {item["id"]: item for item in kpis}


def test_catalog_contains_six_minimum_kpis_with_auditable_contract(calculated_kpis):
    by_id = _by_id(calculated_kpis)

    assert {f"KPI-{index:02d}" for index in range(1, 7)} <= set(by_id)
    for kpi in calculated_kpis:
        assert MANDATORY_FIELDS <= set(kpi)
        assert kpi["variables"]
        assert 0 <= kpi["coverage_pct"] <= 100
        assert isinstance(kpi["limitations"], list)


def test_volume_by_period_tracks_invalid_dates(calculated_kpis):
    kpi = _by_id(calculated_kpis)["KPI-01"]

    assert kpi["value"] == {"2024-01": 2, "2024-02": 1}
    assert kpi["valid_observations"] == 3
    assert kpi["coverage_pct"] == pytest.approx(75.0)
    assert kpi["denominator"] is None


def test_status_percentages_use_non_null_status_as_denominator(calculated_kpis):
    kpi = _by_id(calculated_kpis)["KPI-02"]

    assert kpi["denominator"] == 4
    assert kpi["value"] == {
        "Cancelada": 25.0,
        "Em andamento": 25.0,
        "Finalizada": 50.0,
    }
    assert sum(kpi["value"].values()) == pytest.approx(100.0)


def test_company_coverage_is_computed_for_every_research_with_explicit_denominator(
    calculated_kpis,
):
    kpi = _by_id(calculated_kpis)["KPI-03"]

    assert kpi["denominator"] == 4
    assert kpi["name"] == "Cobertura de empresas cadastradas por pesquisa"
    assert kpi["value"] == {"10": 50.0, "11": 25.0, "12": 25.0, "13": 0.0}
    assert kpi["numerator"] == {"10": 2, "11": 1, "12": 1, "13": 0}
    assert kpi["granularity"] == "pesquisa"
    assert kpi["coverage_unit"] == "linhas de participação"
    assert any("não taxa oficial de adesão" in text for text in kpi["limitations"])


def test_delivery_mean_excludes_negative_and_missing_values(calculated_kpis):
    kpi = _by_id(calculated_kpis)["KPI-04"]

    assert kpi["value"] == pytest.approx(15.0)
    assert kpi["valid_observations"] == 2
    assert kpi["coverage_pct"] == pytest.approx(50.0)
    assert "dias_uteis_para_entrega >= 0" in kpi["filters"]
    assert kpi["name"].startswith("Proxy de tempo médio de entrega")
    assert any("solicitação-publicação" in text for text in kpi["limitations"])


def test_participations_are_counts_not_a_rate_without_invited_population(
    calculated_kpis,
):
    kpi = _by_id(calculated_kpis)["KPI-05"]

    assert kpi["value"] == {"10": 2, "11": 1, "12": 1, "13": 0}
    assert kpi["denominator"] is None
    assert kpi["unit"] == "participações"
    assert kpi["variables"] == ["respondentes.id_pesq", "respondentes.id_empresa"]
    assert kpi["coverage_unit"] == "linhas de participação"
    assert any("denominador" in text.lower() for text in kpi["limitations"])


def test_missingness_kpi_uses_only_declared_critical_fields(calculated_kpis):
    kpi = _by_id(calculated_kpis)["KPI-06"]
    expected_variables = {
        "pesquisas.id",
        "pesquisas.status",
        "pesquisas.data_solicitacao",
        "pesquisas.dias_uteis_para_entrega",
        "empresas.ID",
        "respondentes.id_pesq",
        "respondentes.id_empresa",
    }

    assert set(kpi["variables"]) == expected_variables
    assert kpi["numerator"] == 2
    assert kpi["denominator"] == 28
    assert kpi["value"] == pytest.approx(7.142857142857143)
    assert kpi["name"] == "Micro média de ausência em campos críticos"
    assert kpi["scorecards"]["by_field"]["pesquisas.data_solicitacao"] == {
        "dataset": "pesquisas",
        "field": "data_solicitacao",
        "grain": "pesquisa",
        "missing_cells": 1,
        "expected_cells": 4,
        "missing_pct": 25.0,
        "completeness_pct": 75.0,
    }
    assert kpi["scorecards"]["by_grain"]["pesquisa"] == {
        "dataset": "pesquisas",
        "fields": [
            "pesquisas.id",
            "pesquisas.status",
            "pesquisas.data_solicitacao",
            "pesquisas.dias_uteis_para_entrega",
        ],
        "missing_cells": 2,
        "expected_cells": 16,
        "missing_pct": 12.5,
        "affected_entities": 1,
        "total_entities": 4,
        "affected_entities_pct": 25.0,
    }


def test_company_coverage_excludes_companies_outside_denominator_and_stays_bounded(
    ingestion_api, kpi_api, synthetic_datasets
):
    for index in range(8):
        synthetic_datasets["respondentes"].loc[len(synthetic_datasets["respondentes"])] = {
            "id_pesq": "10",
            "hora_inicio": None,
            "hora_termino": None,
            "id_empresa": f"outside-{index}",
            "market_share": None,
            "id_cliente": "s/i",
        }
    normalized, _ = ingestion_api.normalize_datasets(synthetic_datasets)

    kpi = _by_id(kpi_api.calculate_kpis(normalized))["KPI-03"]

    assert kpi["numerator"]["10"] == 2
    assert kpi["value"]["10"] == 50.0
    assert all(0.0 <= value <= 100.0 for value in kpi["value"].values())
    assert kpi["valid_observations"] == 4
    assert kpi["expected_observations"] == 12
    assert kpi["coverage_pct"] == pytest.approx(100 / 3)


def test_orphan_research_participations_are_excluded_from_business_kpis(
    ingestion_api, kpi_api, synthetic_datasets
):
    synthetic_datasets["respondentes"].loc[len(synthetic_datasets["respondentes"])] = {
        "id_pesq": "999",
        "hora_inicio": None,
        "hora_termino": None,
        "id_empresa": "4",
        "market_share": "40,00%",
        "id_cliente": "s/i",
    }
    normalized, _ = ingestion_api.normalize_datasets(synthetic_datasets)

    by_id = _by_id(kpi_api.calculate_kpis(normalized))
    comparisons = {
        item["indicator_id"]: item
        for item in kpi_api.compare_granularities(normalized)
    }

    assert "999" not in by_id["KPI-03"]["value"]
    assert "999" not in by_id["KPI-05"]["value"]
    assert by_id["KPI-05"]["numerator"] == 4
    assert comparisons["KPI-03"]["values_by_granularity"]["global"] == 75.0
    assert comparisons["KPI-05"]["values_by_granularity"]["global"] == 4


def test_zero_denominator_is_null_not_zero(ingestion_api, kpi_api, synthetic_datasets):
    synthetic_datasets["empresas"] = synthetic_datasets["empresas"].iloc[0:0]
    normalized, _ = ingestion_api.normalize_datasets(synthetic_datasets)

    by_id = _by_id(kpi_api.calculate_kpis(normalized))

    assert by_id["KPI-03"]["denominator"] == 0
    assert by_id["KPI-03"]["value"] is None


def test_respondent_id_is_not_used_to_infer_participation(
    ingestion_api, kpi_api, synthetic_datasets
):
    normalized, _ = ingestion_api.normalize_datasets(synthetic_datasets)
    baseline = _by_id(kpi_api.calculate_kpis(normalized))["KPI-05"]["value"]
    synthetic_datasets["respostas"]["respondent_id"] = ["x", "x", "x", "x"]
    normalized_changed, _ = ingestion_api.normalize_datasets(synthetic_datasets)

    changed = _by_id(kpi_api.calculate_kpis(normalized_changed))["KPI-05"]["value"]
    assert changed == baseline


def test_two_indicators_are_compared_at_multiple_granularities(
    ingestion_api, kpi_api, synthetic_datasets
):
    normalized, _ = ingestion_api.normalize_datasets(synthetic_datasets)

    comparisons = {
        item["indicator_id"]: item
        for item in kpi_api.compare_granularities(normalized)
    }

    assert set(comparisons) >= {"KPI-03", "KPI-05"}
    assert comparisons["KPI-03"]["values_by_granularity"] == {
        "global": 75.0,
        "pesquisa": {"10": 50.0, "11": 25.0, "12": 25.0, "13": 0.0},
    }
    assert comparisons["KPI-05"]["values_by_granularity"] == {
        "global": 4,
        "pesquisa": {"10": 2, "11": 1, "12": 1, "13": 0},
        "empresa": {"1": 1, "2": 2, "3": 1},
    }
    for comparison in comparisons.values():
        assert comparison["denominator_note"]
        assert comparison["weighting_note"]
