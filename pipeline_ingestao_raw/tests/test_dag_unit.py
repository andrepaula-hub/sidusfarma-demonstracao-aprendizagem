from __future__ import annotations

import pytest


def test_csv_parser_preserves_partner_values_and_ignores_unnamed_column(dag_module):
    rows = dag_module._csv_rows(b"id;valor;;\n001;s/i;ignorar\n")
    assert rows == [{"id": "001", "valor": "s/i"}]


def test_csv_parser_rejects_file_without_named_header(dag_module):
    with pytest.raises(ValueError, match="cabeçalho"):
        dag_module._csv_rows(b";;\n1;2;3\n")


def test_dag_has_schedule_retry_and_failure_audit_callback(dag_module):
    dag = dag_module.ingestao_raw_sindusfarma()
    assert dag.schedule_interval is not None
    assert dag.default_args["retries"] == 2
    assert dag.max_active_runs == 1
    assert dag.on_failure_callback is dag_module._registrar_falha


def test_required_source_error_is_clear_and_happens_before_load(dag_module, monkeypatch):
    class MissingObject(Exception):
        pass

    class Client:
        class exceptions:
            NoSuchKey = MissingObject

        def get_object(self, **_):
            raise MissingObject()

    monkeypatch.setattr(dag_module, "_s3", lambda: Client())
    dag = dag_module.ingestao_raw_sindusfarma()
    with pytest.raises(ValueError, match="Arquivo obrigatório ausente"):
        dag.task_dict["validar_arquivos"].python_callable()


def test_observability_contract_covers_volume_time_and_quality(dag_module):
    source = dag_module.__file__
    text = open(source, encoding="utf-8").read()
    for metric in (
        "validation_seconds",
        "load_seconds",
        "transform_seconds",
        "duration_seconds",
        "rows_read",
        "rows_inserted",
        "rows_replayed",
        "quarantine_rows",
    ):
        assert metric in text


def test_audit_versioning_uses_the_manifest_checksum_key(dag_module):
    source = open(dag_module.__file__, encoding="utf-8").read()
    assert 'dataset: values["checksum"]' in source
    assert 'dataset: values["source_checksum"]' not in source
