from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
_configured_dags = Path(os.getenv("AIRFLOW_DAGS_FOLDER", ""))
_mounted_dags = Path("/opt/airflow/dags")
_dag_dir = _configured_dags if (_configured_dags / "ingestao_raw.py").is_file() else _mounted_dags
DAG_FILE = _dag_dir / "ingestao_raw.py"
if not DAG_FILE.is_file():
    DAG_FILE = ROOT / "airflow" / "dags" / "ingestao_raw.py"


@pytest.fixture(scope="session")
def dag_module():
    spec = importlib.util.spec_from_file_location("ingestao_raw_under_test", DAG_FILE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
