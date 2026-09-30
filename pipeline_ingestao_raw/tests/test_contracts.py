"""Gates de contrato: todo requisito documentado vira uma verificação executável."""
from __future__ import annotations

import csv
import os
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
CONTRACTS = Path(os.getenv("CONTRACT_DIR", ROOT.parent / "contracts"))
DATA = ROOT / "data"


def _contract(name: str) -> dict:
    return yaml.safe_load((CONTRACTS / name).read_text(encoding="utf-8"))


def test_raw_contract_matches_the_six_partner_files_and_encoding():
    contract = _contract("contrato_fontes_raw.yml")
    for source in contract["sources"]:
        path = DATA / source["file_name"]
        assert path.exists(), f"fonte contratada ausente: {path.name}"
        header = next(csv.reader(path.open(encoding=source["expected_encoding"]), delimiter=source["expected_delimiter"]))
        assert set(source["primary_key"]).issubset(header), source["dataset"]


def test_staging_contract_required_fields_exist_in_the_source_header():
    raw = _contract("contrato_fontes_raw.yml")
    staging = _contract("contrato_staging.yml")
    for source in raw["sources"]:
        header = next(csv.reader((DATA / source["file_name"]).open(encoding="utf-8-sig"), delimiter=";"))
        missing = set(staging["datasets"][source["dataset"]]["required_fields"]) - set(header)
        assert not missing, f"{source['dataset']}: {sorted(missing)}"


def test_complete_data_mapping_covers_all_source_columns_or_explicit_raw_retention():
    mapping = (ROOT / "DATA_MAPPING.md").read_text(encoding="utf-8")
    for path in DATA.glob("*.csv"):
        header = next(csv.reader(path.open(encoding="utf-8-sig"), delimiter=";"))
        for field in {item for item in header if item}:
            assert f"`{field}`" in mapping, f"campo sem linhagem documentada: {path.name}.{field}"


def test_dw_contract_models_are_present_and_documented_in_dbt():
    contract = _contract("contrato_dw_analytics.yml")
    schema = (ROOT / "dbt/models/schema.yml").read_text(encoding="utf-8")
    for model in contract["models"]:
        assert (ROOT / "dbt/models/trusted" / f"{model['model_name']}.sql").exists()
        assert f"name: {model['model_name']}" in schema
