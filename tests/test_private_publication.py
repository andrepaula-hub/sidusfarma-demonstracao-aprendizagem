"""Contratos do pacote privado e do bloqueio de publicação."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.publication.prepare_private_site import prepare_private_site
from scripts.publication.privacy_gate import validate_private_site


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_private_source_is_built_only_from_explicit_allowlist(tmp_path):
    destination = PROJECT_ROOT / ".build" / f"test-private-{tmp_path.name}"
    files = prepare_private_site(destination=destination)
    relative = {path.relative_to(destination).as_posix() for path in files}

    assert len(relative) == 11
    assert "index.md" in relative
    assert "modelagem_quantitativa_de_dados_do_parceiro.md" in relative
    assert sum(path.startswith("images/") for path in relative) == 7
    assert not any(path.startswith("data/") for path in relative)
    report = (destination / "modelagem_quantitativa_de_dados_do_parceiro.md").read_text(
        encoding="utf-8"
    )
    assert "(data/quality_report.json)" not in report
    assert "(data/kpis_summary.json)" not in report


def test_preparer_rejects_destination_outside_build(tmp_path):
    with pytest.raises(ValueError, match=r"subdiretório de \.build"):
        prepare_private_site(destination=tmp_path / "unsafe")


def test_preparer_rejects_unknown_source_in_manifest(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "files": [
                    {"source": "REFERENCE_MATERIAL/segredo.csv", "destination": "segredo.csv"}
                ],
            }
        ),
        encoding="utf-8",
    )
    destination = PROJECT_ROOT / ".build" / f"test-invalid-{tmp_path.name}"
    with pytest.raises(ValueError, match="Fonte fora das áreas permitidas"):
        prepare_private_site(manifest, destination)


def test_privacy_gate_rejects_raw_file_and_personal_email(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text(
        "<p>pessoa@example.com</p>", encoding="utf-8"
    )
    (site / "dados.csv").write_text("segredo", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        validate_private_site(site)

    assert "extensão proibida" in str(exc.value)
    assert "padrão proibido" in str(exc.value)


def test_privacy_gate_accepts_minimal_aggregate_site(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text(
        "<h1>Resultados agregados</h1>", encoding="utf-8"
    )

    assert validate_private_site(site) == []
