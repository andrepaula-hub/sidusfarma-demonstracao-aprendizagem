"""Testes reais contra os serviços Docker; execute com RUN_PIPELINE_INTEGRATION=1."""
from __future__ import annotations

import os
import subprocess

import pytest
from airflow.providers.postgres.hooks.postgres import PostgresHook


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_PIPELINE_INTEGRATION") != "1",
    reason="requer MinIO, PostgreSQL, Airflow e dbt ativos via Docker Compose",
)


def test_dbt_models_and_quality_tests_pass():
    result = subprocess.run(
        ["dbt", "build", "--project-dir", "/opt/airflow/dbt"],
        env={**os.environ, "DBT_PROFILES_DIR": "/opt/airflow/dbt"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_last_successful_run_has_auditable_metrics():
    connection = PostgresHook(postgres_conn_id="warehouse").get_conn()
    with connection.cursor() as cursor:
        cursor.execute(
            """select status, metrics from audit.audit_pipeline_runs
               where status = 'success' order by finished_at desc limit 1"""
        )
        row = cursor.fetchone()
    connection.close()
    assert row, "execute a DAG antes de rodar este teste"
    status, metrics = row
    assert status == "success"
    assert metrics["duration_seconds"] >= 0
    assert metrics["staging"]
    assert "quarantine_rows" in metrics
