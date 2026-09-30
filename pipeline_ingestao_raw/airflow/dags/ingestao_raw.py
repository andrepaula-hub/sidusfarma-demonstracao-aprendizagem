"""DAG idempotente para CSVs Sindusfarma em MinIO, PostgreSQL e dbt."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import boto3
import yaml
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import Json, execute_values

DATASETS = ("clientes", "empresas", "pesquisas", "questoes", "respondentes", "respostas")
BUCKET = "raw"
PIPELINE_SCHEDULE = os.getenv("PIPELINE_SCHEDULE", "0 */6 * * *")
PIPELINE_VERSION = os.getenv("PIPELINE_VERSION", "1.0.0")
CONTRACT_DIR = Path(os.getenv("CONTRACT_DIR", "/opt/airflow/contracts"))
LOGGER = logging.getLogger(__name__)


def _s3():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
        region_name="us-east-1",
    )


def _warehouse():
    return PostgresHook(postgres_conn_id="warehouse").get_conn()


def _csv_rows(body: bytes):
    """Lê CSV do parceiro e elimina somente colunas sem nome de preenchimento."""
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig")), delimiter=";")
    fields = reader.fieldnames or []
    if not any(field and field.strip() for field in fields):
        raise ValueError("CSV sem cabeçalho nomeado")
    return [{key: value for key, value in row.items() if key and key.strip()} for row in reader]


def _contract_requirements() -> dict:
    """Lê os contratos versionados, evitando regras de cabeçalho divergentes no código."""
    raw = yaml.safe_load((CONTRACT_DIR / "contrato_fontes_raw.yml").read_text(encoding="utf-8"))
    staging = yaml.safe_load((CONTRACT_DIR / "contrato_staging.yml").read_text(encoding="utf-8"))
    raw_sources = {source["dataset"]: source for source in raw["sources"]}
    return {
        dataset: {
            "file_name": source["file_name"],
            "encoding": source["expected_encoding"],
            "delimiter": source["expected_delimiter"],
            "required_fields": staging["datasets"][dataset]["required_fields"],
            "contract_version": raw["contract_version"],
        }
        for dataset, source in raw_sources.items()
    }


def _validate_contract_header(dataset: str, body: bytes) -> int:
    """Falha antes da carga se arquivo divergir do contrato raw/staging."""
    requirement = _contract_requirements()[dataset]
    reader = csv.reader(io.StringIO(body.decode(requirement["encoding"])), delimiter=requirement["delimiter"])
    header = next(reader, [])
    named_columns = {name.strip() for name in header if name and name.strip()}
    missing = set(requirement["required_fields"]) - named_columns
    if missing:
        raise ValueError(
            f"Contrato staging violado em {dataset}: campos obrigatórios ausentes: {', '.join(sorted(missing))}"
        )
    return len(named_columns)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _structured_log(event: str, **fields) -> None:
    """Emite log JSON pesquisável no Airflow sem incluir conteúdo do parceiro."""
    LOGGER.info(json.dumps({"event": event, **fields}, ensure_ascii=False, default=str))


def _bootstrap(connection):
    with connection.cursor() as cursor:
        cursor.execute("create schema if not exists raw_staging")
        cursor.execute("create schema if not exists audit")
        cursor.execute(
            """create table if not exists audit.audit_pipeline_runs (
                run_id text primary key, started_at timestamptz not null default now(),
                finished_at timestamptz, status text not null,
                failure_reason text, metrics jsonb not null default '{}'::jsonb
            )"""
        )
        cursor.execute(
            "alter table audit.audit_pipeline_runs add column if not exists failure_reason text"
        )
        for dataset in DATASETS:
            cursor.execute(
                f'''create table if not exists raw_staging.{dataset}_raw (
                    dataset_name text not null, source_file text not null, source_checksum text not null,
                    source_row_number integer not null, raw_payload jsonb not null, run_id text not null,
                    ingested_at timestamptz not null default now(),
                    primary key (dataset_name, source_checksum, source_row_number)
                )'''
            )
    connection.commit()


def _registrar_falha(context) -> None:
    """Fecha a auditoria quando a DAG termina em falha, inclusive após retries."""
    dag_run = context.get("dag_run")
    if dag_run is None:
        return
    run_id = dag_run.run_id
    reason = str(context.get("exception") or "falha da DAG")[:1000]
    try:
        connection = _warehouse()
        _bootstrap(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """insert into audit.audit_pipeline_runs
                   (run_id, status, finished_at, failure_reason)
                   values (%s, 'failed', now(), %s)
                   on conflict (run_id) do update set status = 'failed',
                   finished_at = now(), failure_reason = excluded.failure_reason""",
                (run_id, reason),
            )
        connection.commit()
        connection.close()
        _push_failure_status()
        _structured_log("pipeline_failed", run_id=run_id, reason=reason)
    except Exception:  # Nunca ocultar a causa original da falha do pipeline.
        LOGGER.exception("Não foi possível registrar a falha da execução %s", run_id)


def _push_failure_status() -> None:
    endpoint = os.getenv("PUSHGATEWAY_URL")
    if not endpoint:
        return
    try:
        from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

        registry = CollectorRegistry()
        Gauge("etl_pipeline_status", "1 para execução bem-sucedida", registry=registry).set(0)
        push_to_gateway(
            endpoint,
            job="sindusfarma_etl",
            registry=registry,
            grouping_key={"pipeline": "ingestao_raw_sindusfarma"},
        )
    except Exception:
        LOGGER.exception("Falha ao publicar o status de erro no Pushgateway")


def _push_observability(run_id: str, metrics: dict) -> None:
    """Publica gauges no Pushgateway; indisponibilidade do monitoramento não perde a carga."""
    endpoint = os.getenv("PUSHGATEWAY_URL")
    if not endpoint:
        return
    try:
        from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

        registry = CollectorRegistry()
        Gauge("etl_pipeline_duration_seconds", "Duração total da execução", registry=registry).set(
            metrics["duration_seconds"]
        )
        Gauge("etl_pipeline_status", "1 para execução bem-sucedida", registry=registry).set(1)
        rows_read = Gauge("etl_rows_read", "Linhas lidas", ["dataset"], registry=registry)
        rows_inserted = Gauge("etl_rows_inserted", "Linhas novas persistidas", ["dataset"], registry=registry)
        rows_replayed = Gauge("etl_rows_replayed", "Linhas já existentes", ["dataset"], registry=registry)
        for dataset, values in metrics["staging"].items():
            labels = {"dataset": dataset}
            rows_read.labels(**labels).set(values["rows_read"])
            rows_inserted.labels(**labels).set(values["rows_inserted"])
            rows_replayed.labels(**labels).set(values["rows_replayed"])
        Gauge("etl_rows_quarantined", "Linhas em quarentena", registry=registry).set(metrics["quarantine_rows"])
        push_to_gateway(
            endpoint,
            job="sindusfarma_etl",
            registry=registry,
            grouping_key={"pipeline": "ingestao_raw_sindusfarma"},
        )
    except Exception:
        LOGGER.exception("Falha ao publicar métricas no Pushgateway para %s", run_id)


@dag(
    dag_id="ingestao_raw_sindusfarma",
    start_date=datetime(2026, 1, 1),
    schedule=PIPELINE_SCHEDULE,
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2},
    on_failure_callback=_registrar_falha,
    tags=["sindusfarma", "raw", "dbt"],
)
def ingestao_raw_sindusfarma():
    @task
    def iniciar_auditoria():
        run_id = get_current_context()["run_id"]
        connection = _warehouse()
        _bootstrap(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """insert into audit.audit_pipeline_runs (run_id, status)
                   values (%s, 'running')
                   on conflict (run_id) do update set status = 'running', started_at = now(),
                   finished_at = null, failure_reason = null, metrics = '{}'::jsonb""",
                (run_id,),
            )
        connection.commit()
        connection.close()
        _structured_log("pipeline_started", run_id=run_id, started_at=_utc_now())

    @task
    def validar_arquivos():
        started = perf_counter()
        client, manifest = _s3(), {}
        for dataset in DATASETS:
            key = f"raw/{dataset}/ano=2026/{dataset}.csv"
            try:
                body = client.get_object(Bucket=BUCKET, Key=key)["Body"].read()
            except client.exceptions.NoSuchKey as error:
                raise ValueError(f"Arquivo obrigatório ausente: s3://{BUCKET}/{key}") from error
            checksum = hashlib.sha256(body).hexdigest()
            column_count = _validate_contract_header(dataset, body)
            rows = _csv_rows(body)
            manifest[dataset] = {
                "key": key,
                "checksum": checksum,
                "bytes": len(body),
                "rows": len(rows),
                "columns": column_count,
                "contract_version": _contract_requirements()[dataset]["contract_version"],
            }
        result = {
            "manifest": manifest,
            "validation_seconds": round(perf_counter() - started, 6),
            "source_bytes": sum(item["bytes"] for item in manifest.values()),
        }
        _structured_log("source_validated", datasets=len(manifest), **result)
        return result

    @task
    def carregar_staging(validation: dict):
        started = perf_counter()
        manifest = validation["manifest"]
        run_id, client, connection = get_current_context()["run_id"], _s3(), _warehouse()
        totals = {}
        for dataset, metadata in manifest.items():
            body = client.get_object(Bucket=BUCKET, Key=metadata["key"])["Body"].read()
            rows = _csv_rows(body)
            values = [
                (dataset, metadata["key"], metadata["checksum"], index, Json(row), run_id)
                for index, row in enumerate(rows, start=2)
            ]
            with connection.cursor() as cursor:
                cursor.execute(
                    f"select count(*) from raw_staging.{dataset}_raw where dataset_name = %s and source_checksum = %s",
                    (dataset, metadata["checksum"]),
                )
                before_count = cursor.fetchone()[0]
                execute_values(
                    cursor,
                    f"insert into raw_staging.{dataset}_raw (dataset_name, source_file, source_checksum, source_row_number, raw_payload, run_id) values %s on conflict do nothing",
                    values,
                )
                cursor.execute(
                    f"select count(*) from raw_staging.{dataset}_raw where dataset_name = %s and source_checksum = %s",
                    (dataset, metadata["checksum"]),
                )
                inserted = cursor.fetchone()[0] - before_count
                totals[dataset] = {
                    "rows_read": len(rows),
                    "rows_inserted": inserted,
                    "rows_replayed": len(rows) - inserted,
                    "rows_rejected": 0,
                }
            connection.commit()
        connection.close()
        result = {
            "staging": totals,
            "load_seconds": round(perf_counter() - started, 6),
            "validation_seconds": validation["validation_seconds"],
            "source_bytes": validation["source_bytes"],
        }
        _structured_log("raw_loaded", **result)
        return result

    @task
    def dbt_build_e_docs():
        started = perf_counter()
        environment = {**os.environ, "DBT_PROFILES_DIR": "/opt/airflow/dbt"}
        for command in (["dbt", "build", "--project-dir", "/opt/airflow/dbt"], ["dbt", "docs", "generate", "--project-dir", "/opt/airflow/dbt"]):
            subprocess.run(command, check=True, env=environment)
        result = {"transform_seconds": round(perf_counter() - started, 6)}
        _structured_log("dbt_completed", **result)
        return result

    @task(trigger_rule="all_success")
    def registrar_metricas(load_result: dict, dbt_result: dict):
        run_id, connection = get_current_context()["run_id"], _warehouse()
        with connection.cursor() as cursor:
            cursor.execute("select count(*) from trusted_dw.fato_resposta")
            trusted = cursor.fetchone()[0]
            cursor.execute("select count(*) from quarantine.quarantine_registros_orfaos")
            quarantine = cursor.fetchone()[0]
            cursor.execute(
                "select extract(epoch from (now() - started_at)) from audit.audit_pipeline_runs where run_id = %s",
                (run_id,),
            )
            duration = float(cursor.fetchone()[0])
            metrics = {
                "staging": load_result["staging"],
                "source_bytes": load_result["source_bytes"],
                "pipeline_version": PIPELINE_VERSION,
                "contract_version": "1.0.0",
                "dataset_versions": {
                    dataset: values["checksum"]
                    for dataset, values in get_current_context().get("ti").xcom_pull(
                        task_ids="validar_arquivos"
                    )["manifest"].items()
                },
                "validation_seconds": load_result["validation_seconds"],
                "load_seconds": load_result["load_seconds"],
                "transform_seconds": dbt_result["transform_seconds"],
                "duration_seconds": round(duration, 6),
                "trusted_fato_resposta": trusted,
                "quarantine_rows": quarantine,
                "status": "success",
            }
            cursor.execute(
                "update audit.audit_pipeline_runs set status = 'success', finished_at = now(), metrics = %s where run_id = %s",
                (Json(metrics), run_id),
            )
        connection.commit()
        connection.close()
        _push_observability(run_id, metrics)
        _structured_log("pipeline_completed", run_id=run_id, **metrics)
        return metrics

    started = iniciar_auditoria()
    manifest = validar_arquivos()
    loaded = carregar_staging(manifest)
    docs = dbt_build_e_docs()
    started >> manifest >> loaded >> docs
    registrar_metricas(loaded, docs)


ingestao_raw_sindusfarma()
