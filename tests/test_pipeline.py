"""Testes do fluxo completo, contratos publicados e privacidade."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest
import matplotlib.image as mpimg


FIXED_TIMESTAMP = datetime(2026, 8, 13, 12, 0, tzinfo=timezone.utc)


def _strict_json(path: Path):
    def reject_constant(value):
        raise ValueError(f"Constante JSON não permitida: {value}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def _published_text(output_dir: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in output_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".log"}
    )


def test_full_pipeline_writes_strict_versioned_contracts_and_charts(
    runner_api, synthetic_source_dir, tmp_path
):
    output_dir = tmp_path / "published"

    result = runner_api.run_analysis(
        source_dir=synthetic_source_dir,
        output_dir=output_dir,
        generated_at=FIXED_TIMESTAMP,
        snapshot_date="2026-08-13",
    )

    quality_path = output_dir / "quality_report.json"
    kpis_path = output_dir / "kpis_summary.json"
    quality = _strict_json(quality_path)
    kpis = _strict_json(kpis_path)

    assert quality["schema_version"] == "2.0"
    assert kpis["schema_version"] == "2.0"
    assert quality["contract_schema"] == "schemas/quality-report-v2.schema.json"
    assert kpis["contract_schema"] == "schemas/kpis-summary-v2.schema.json"
    assert quality["generated_at"] == "2026-08-13T12:00:00+00:00"
    assert quality["source_manifest"]["canonical_format"] == "csv-provisional"
    assert quality["source_manifest"]["snapshot_date"] == "2026-08-13"
    assert set(quality["source_manifest"]["files"]) == {
        "clientes",
        "empresas",
        "pesquisas",
        "questoes",
        "respondentes",
        "respostas",
    }
    assert all(
        len(item["sha256"]) == 64
        for item in quality["source_manifest"]["files"].values()
    )
    assert set(quality["datasets"]) == {
        "clientes",
        "empresas",
        "pesquisas",
        "questoes",
        "respondentes",
        "respostas",
    }
    assert len(quality["relationships"]) == 8
    assert len(kpis["kpis"]) >= 6
    assert {
        item["indicator_id"] for item in kpis["granularity_analysis"]
    } >= {"KPI-03", "KPI-05"}
    assert result["quality_report"] == quality_path
    assert result["kpis_summary"] == kpis_path
    assert len(result["charts"]) == 7
    assert all(path.suffix.lower() == ".png" and path.stat().st_size > 0 for path in result["charts"])
    for chart_path in result["charts"]:
        pixels = mpimg.imread(chart_path)
        assert pixels.shape[0] >= 700
        assert pixels.shape[1] >= 1000
        assert float(pixels.std()) > 0.02


def test_pipeline_is_deterministic_for_same_data_code_and_timestamp(
    runner_api, synthetic_source_dir, tmp_path
):
    first = tmp_path / "first"
    second = tmp_path / "second"

    runner_api.run_analysis(synthetic_source_dir, first, generated_at=FIXED_TIMESTAMP)
    runner_api.run_analysis(synthetic_source_dir, second, generated_at=FIXED_TIMESTAMP)

    assert _strict_json(first / "quality_report.json") == _strict_json(
        second / "quality_report.json"
    )
    assert _strict_json(first / "kpis_summary.json") == _strict_json(
        second / "kpis_summary.json"
    )


def test_pipeline_rejects_ambiguous_snapshot_date_before_reading_sources(
    runner_api, synthetic_source_dir, tmp_path
):
    with pytest.raises(ValueError, match="AAAA-MM-DD"):
        runner_api.run_analysis(
            synthetic_source_dir,
            tmp_path / "invalid-snapshot",
            snapshot_date="13/08/2026",
        )


def test_published_outputs_do_not_expose_personal_or_individual_values(
    runner_api, synthetic_source_dir, tmp_path, caplog
):
    output_dir = tmp_path / "private-check"
    runner_api.run_analysis(synthetic_source_dir, output_dir, generated_at=FIXED_TIMESTAMP)

    published = _published_text(output_dir)
    for private_value in {
        "alpha@example.invalid",
        "beta@example.invalid",
        "gamma@example.invalid",
        "texto sintético",
        "r-a",
        "r-b",
        "r-c",
    }:
        assert private_value not in published
        assert private_value not in caplog.text
    assert str(synthetic_source_dir.resolve()) not in published


def test_failure_does_not_leave_partial_publication(
    runner_api, synthetic_source_dir, tmp_path
):
    (synthetic_source_dir / "pesquisas.csv").unlink()
    output_dir = tmp_path / "partial"
    output_dir.mkdir()
    sentinel = output_dir / "previous-success.txt"
    sentinel.write_text("resultado anterior preservado", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match=r"pesquisas\.csv"):
        runner_api.run_analysis(synthetic_source_dir, output_dir)

    assert {path.name for path in output_dir.iterdir()} == {sentinel.name}
    assert sentinel.read_text(encoding="utf-8") == "resultado anterior preservado"


def test_publish_transaction_restores_every_previous_output_after_mid_publish_failure(
    runner_api, tmp_path, monkeypatch
):
    staging = tmp_path / "staging"
    staging.mkdir()
    first_staged = staging / "first.new"
    second_staged = staging / "second.new"
    first_staged.write_text("novo primeiro", encoding="utf-8")
    second_staged.write_text("novo segundo", encoding="utf-8")

    published = tmp_path / "published"
    published.mkdir()
    first_target = published / "first.txt"
    second_target = published / "second.txt"
    first_target.write_text("antigo primeiro", encoding="utf-8")
    second_target.write_text("antigo segundo", encoding="utf-8")

    real_replace = os.replace
    failed = False

    def fail_once_during_publication(source, target):
        nonlocal failed
        if Path(source) == second_staged and not failed:
            failed = True
            raise OSError("falha injetada durante publicação")
        real_replace(source, target)

    monkeypatch.setattr(
        "scripts.runners.run_full_analysis.os.replace",
        fail_once_during_publication,
    )

    with pytest.raises(OSError, match="falha injetada"):
        runner_api.publish_transaction(
            [(first_staged, first_target), (second_staged, second_target)],
            staging,
        )

    assert first_target.read_text(encoding="utf-8") == "antigo primeiro"
    assert second_target.read_text(encoding="utf-8") == "antigo segundo"


def test_duplicate_question_key_is_reported_without_crashing_pipeline(
    runner_api, synthetic_source_dir, tmp_path
):
    import pandas as pd

    questions_path = synthetic_source_dir / "questoes.csv"
    questions = pd.read_csv(
        questions_path,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=False,
    )
    questions = pd.concat([questions, questions.iloc[[0]]], ignore_index=True)
    questions.to_csv(
        questions_path,
        sep=";",
        encoding="utf-8-sig",
        index=False,
    )

    output_dir = tmp_path / "duplicate-question"
    runner_api.run_analysis(
        synthetic_source_dir,
        output_dir,
        generated_at=FIXED_TIMESTAMP,
    )
    quality = _strict_json(output_dir / "quality_report.json")
    check = next(
        item
        for item in quality["consistency_checks"]
        if item["id"] == "questoes_id_pergunta_duplicado"
    )

    assert check["severity"] == "error"
    assert check["affected_row_count"] == 2


def test_versioned_contract_schemas_are_valid_json_and_cover_envelopes():
    project_root = Path(__file__).resolve().parents[1]
    quality_schema = _strict_json(
        project_root / "docs/data/schemas/quality-report-v2.schema.json"
    )
    kpis_schema = _strict_json(
        project_root / "docs/data/schemas/kpis-summary-v2.schema.json"
    )

    assert quality_schema["$schema"].endswith("2020-12/schema")
    assert kpis_schema["$schema"].endswith("2020-12/schema")
    assert "response_representations" in quality_schema["required"]
    assert "kpis" in kpis_schema["required"]
