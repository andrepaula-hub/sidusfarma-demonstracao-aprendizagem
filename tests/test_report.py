"""Contratos documentais do relatório final do Artefato 3."""

from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_PATH = DOCS_DIR / "modelagem_quantitativa_de_dados_do_parceiro.md"


def _markdown_targets(markdown: str) -> list[str]:
    return re.findall(r"!?\[[^]]*\]\(([^)]+)\)", markdown)


def test_report_has_the_six_required_sections_and_kpis():
    report = REPORT_PATH.read_text(encoding="utf-8")
    required_sections = (
        "## 1. Contextualização quantitativa",
        "## 2. Unidades de análise e variáveis",
        "## 3. Qualidade dos dados",
        "## 4. Estatística descritiva",
        "## 5. Indicadores iniciais",
        "## 6. Granularidade e síntese final",
    )

    assert all(report.count(section) == 1 for section in required_sections)
    assert all(report.count(f"### KPI-{index:02d} —") == 1 for index in range(1, 7))
    assert report.count("![") >= 6


def test_report_uses_the_same_six_kpi_contracts_as_the_pipeline():
    report = REPORT_PATH.read_text(encoding="utf-8")
    payload = json.loads(
        (DOCS_DIR / "data" / "kpis_summary.json").read_text(encoding="utf-8")
    )

    assert [item["id"] for item in payload["kpis"]] == [
        f"KPI-{index:02d}" for index in range(1, 7)
    ]
    assert "18.680 participações válidas" in report
    assert "0,0982%" in report
    assert "55 participações órfãs" in report


def test_internal_report_and_index_links_resolve():
    for source in (REPORT_PATH, DOCS_DIR / "index.md"):
        markdown = source.read_text(encoding="utf-8")
        for target in _markdown_targets(markdown):
            if target.startswith(("#", "http://", "https://")):
                continue
            resolved = (source.parent / target.split("#", 1)[0]).resolve()
            assert resolved.exists(), f"Link quebrado em {source.name}: {target}"


def test_report_does_not_reintroduce_stale_or_private_source_references():
    report = REPORT_PATH.read_text(encoding="utf-8")
    forbidden = ("DADOS/", "catalogo_reports", "legacy/streamlit", "41 KPIs")

    assert not any(term in report for term in forbidden)
