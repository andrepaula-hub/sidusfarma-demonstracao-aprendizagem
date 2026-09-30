"""Contratos de ingestão, schema e normalização das fontes."""

from __future__ import annotations

import hashlib

import pandas as pd
import pytest


EXPECTED_DATASETS = {
    "clientes",
    "empresas",
    "pesquisas",
    "questoes",
    "respondentes",
    "respostas",
}


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_loads_six_semicolon_utf8_csvs_without_mutating_sources(
    ingestion_api, synthetic_source_dir
):
    before = {path.name: _digest(path) for path in synthetic_source_dir.glob("*.csv")}

    datasets = ingestion_api.load_datasets(synthetic_source_dir)

    after = {path.name: _digest(path) for path in synthetic_source_dir.glob("*.csv")}
    assert set(datasets) == EXPECTED_DATASETS
    assert datasets["clientes"].loc[0, "e-mail"] == "alpha@example.invalid"
    assert datasets["clientes"].loc[3, "id_cliente"] == "s/i"
    assert before == after


def test_missing_required_source_fails_before_analysis(ingestion_api, synthetic_source_dir):
    (synthetic_source_dir / "respostas.csv").unlink()

    with pytest.raises(FileNotFoundError, match=r"respostas\.csv"):
        ingestion_api.load_datasets(synthetic_source_dir)


def test_missing_required_column_identifies_dataset_and_column(
    ingestion_api, synthetic_source_dir
):
    clientes_path = synthetic_source_dir / "clientes.csv"
    clientes = pd.read_csv(clientes_path, sep=";", encoding="utf-8-sig")
    clientes.drop(columns=["id_cliente"]).to_csv(
        clientes_path, sep=";", index=False, encoding="utf-8-sig"
    )

    with pytest.raises(ValueError, match=r"clientes.*id_cliente"):
        ingestion_api.load_datasets(synthetic_source_dir)


def test_loader_preserves_leading_zero_identifiers(
    ingestion_api, synthetic_source_dir
):
    empresas_path = synthetic_source_dir / "empresas.csv"
    empresas = pd.read_csv(empresas_path, sep=";", encoding="utf-8-sig", dtype=str)
    empresas.loc[0, "ID"] = "001"
    empresas.to_csv(empresas_path, sep=";", index=False, encoding="utf-8-sig")

    datasets = ingestion_api.load_datasets(synthetic_source_dir)

    assert datasets["empresas"].loc[0, "ID"] == "001"
    assert datasets["empresas"]["ID"].dtype.name in {"object", "string"}


def test_loader_preserves_non_empty_textual_na_sentinels(
    ingestion_api, synthetic_source_dir
):
    respostas_path = synthetic_source_dir / "respostas.csv"
    respostas = pd.read_csv(
        respostas_path,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=False,
    )
    template = respostas.iloc[[0] * 6].reset_index(drop=True)
    template["id_resposta"] = [f"sentinel-{index}" for index in range(6)]
    template["valor"] = ["NA", "N/A", "null", "None", "#N/A", ""]
    template.to_csv(
        respostas_path,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    loaded = ingestion_api.load_datasets(synthetic_source_dir)["respostas"]

    assert loaded["valor"].iloc[:5].tolist() == [
        "NA",
        "N/A",
        "null",
        "None",
        "#N/A",
    ]
    assert pd.isna(loaded["valor"].iloc[5])


def test_loader_treats_whitespace_only_as_physical_absence(
    ingestion_api, synthetic_source_dir
):
    respostas_path = synthetic_source_dir / "respostas.csv"
    respostas = pd.read_csv(
        respostas_path,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=False,
    )
    respostas.loc[0, "valor"] = "   "
    respostas.to_csv(
        respostas_path,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    loaded = ingestion_api.load_datasets(synthetic_source_dir)["respostas"]

    assert pd.isna(loaded.loc[0, "valor"])


def test_clean_research_schema_does_not_require_empty_unnamed_columns(
    ingestion_api, synthetic_source_dir
):
    pesquisas_path = synthetic_source_dir / "pesquisas.csv"
    pesquisas = pd.read_csv(
        pesquisas_path,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
    )
    cleaned = pesquisas.drop(
        columns=[column for column in pesquisas if column.startswith("Unnamed:")]
    )
    cleaned.to_csv(
        pesquisas_path,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    loaded = ingestion_api.load_datasets(synthetic_source_dir)

    assert loaded["pesquisas"].shape[1] == 22
    assert not any(
        column.startswith("Unnamed:") for column in loaded["pesquisas"].columns
    )


def test_normalization_uses_day_first_percentage_points_and_preserves_ids(
    ingestion_api, synthetic_datasets
):
    normalized, parsing_errors = ingestion_api.normalize_datasets(synthetic_datasets)

    assert normalized["empresas"].loc[0, "% de mercado"] == pytest.approx(10.0)
    assert normalized["respondentes"].loc[1, "market_share"] == pytest.approx(20.0)
    assert normalized["pesquisas"].loc[1, "data_solicitacao"] == pd.Timestamp(
        "2024-01-15"
    )
    assert pd.isna(normalized["pesquisas"].loc[3, "data_solicitacao"])
    assert normalized["clientes"].loc[3, "id_cliente"] == "s/i"
    assert normalized["empresas"].loc[0, "ID"] == "1"
    assert {
        (error["dataset"], error["column"], error["invalid_count"])
        for error in parsing_errors
    } >= {("pesquisas", "data_solicitacao", 1)}


def test_normalization_does_not_mutate_input_frames(ingestion_api, synthetic_datasets):
    originals = {name: frame.copy(deep=True) for name, frame in synthetic_datasets.items()}

    ingestion_api.normalize_datasets(synthetic_datasets)

    for name, original in originals.items():
        pd.testing.assert_frame_equal(synthetic_datasets[name], original)


def test_invalid_percentage_is_null_and_reported(ingestion_api, synthetic_datasets):
    synthetic_datasets["empresas"].loc[1, "% de mercado"] = "desconhecido"

    normalized, parsing_errors = ingestion_api.normalize_datasets(synthetic_datasets)

    assert pd.isna(normalized["empresas"].loc[1, "% de mercado"])
    assert {
        (error["dataset"], error["column"], error["invalid_count"])
        for error in parsing_errors
    } >= {("empresas", "% de mercado", 1)}
