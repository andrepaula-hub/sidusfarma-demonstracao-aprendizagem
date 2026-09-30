"""Contratos matemáticos da auditoria de qualidade e integridade."""

from __future__ import annotations

import importlib

import pandas as pd
import pytest


def test_dataset_audit_reports_completeness_duplicates_constants_and_key(quality_api):
    frame = pd.DataFrame(
        {
            "id": ["1", "2", "3", "3"],
            "value": [10.0, None, 30.0, 30.0],
            "constant": ["x", "x", "x", "x"],
        }
    )

    result = quality_api.audit_dataset(frame, "sample", primary_key=["id"])

    assert result["row_count"] == 4
    assert result["column_count"] == 3
    assert result["null_count_by_column"]["value"] == 1
    assert result["completeness_pct_by_column"]["value"] == pytest.approx(75.0)
    assert result["duplicate_row_count"] == 1
    assert result["constant_columns"] == ["constant"]
    assert result["primary_key"] == {
        "columns": ["id"],
        "null_row_count": 0,
        "duplicate_row_count": 2,
        "is_unique": False,
    }


def test_empty_dataset_uses_null_instead_of_invented_percentage(quality_api):
    result = quality_api.audit_dataset(
        pd.DataFrame(columns=["id", "value"]), "empty", primary_key=["id"]
    )

    assert result["row_count"] == 0
    assert result["completeness_pct_by_column"] == {"id": None, "value": None}


def test_relationship_counts_distinct_orphans_and_affected_rows(quality_api):
    parent = pd.DataFrame({"id": ["1", "2"]})
    child = pd.DataFrame({"parent_id": ["1", "2", "9", "9", None]})

    result = quality_api.audit_relationship(
        parent,
        child,
        parent_key="id",
        child_key="parent_id",
        parent_name="parent",
        child_name="child",
    )

    assert result["parent"] == "parent.id"
    assert result["child"] == "child.parent_id"
    assert result["orphan_value_count"] == 1
    assert result["orphan_row_count"] == 2
    assert result["orphan_values_sample"] == ["9"]


def test_relationship_ignores_null_foreign_keys(quality_api):
    result = quality_api.audit_relationship(
        pd.DataFrame({"id": ["1"]}),
        pd.DataFrame({"parent_id": ["1", None, None]}),
        parent_key="id",
        child_key="parent_id",
        parent_name="parent",
        child_name="child",
    )

    assert result["orphan_value_count"] == 0
    assert result["orphan_row_count"] == 0


def test_missing_relationship_column_is_an_error_not_false_integrity(quality_api):
    with pytest.raises(ValueError, match=r"child.*parent_id"):
        quality_api.audit_relationship(
            pd.DataFrame({"id": ["1"]}),
            pd.DataFrame({"wrong": ["1"]}),
            parent_key="id",
            child_key="parent_id",
            parent_name="parent",
            child_name="child",
        )


def test_conditional_missingness_separates_raw_and_applicable_absence(quality_api):
    questions = pd.DataFrame(
        {
            "tipo": ["multipla_escolha", "aberta", "multipla_escolha"],
            "alternativas": ["Sim | Não", None, None],
        }
    )
    applicable = questions["tipo"].eq("multipla_escolha")

    result = quality_api.audit_conditional_missingness(
        questions,
        column="alternativas",
        applicability_mask=applicable,
    )

    assert result == {
        "column": "alternativas",
        "total_row_count": 3,
        "raw_missing_count": 2,
        "raw_missing_pct": pytest.approx(200 / 3),
        "applicable_row_count": 2,
        "applicable_missing_count": 1,
        "applicable_missing_pct": pytest.approx(50.0),
    }


def test_conditional_missingness_preserves_textual_sentinel_and_rejects_blank(
    quality_api,
):
    frame = pd.DataFrame({"valor": ["NA", "  ", None]})

    result = quality_api.audit_conditional_missingness(
        frame,
        column="valor",
        applicability_mask=pd.Series([True, True, True]),
    )

    assert result["raw_missing_count"] == 2
    assert result["applicable_missing_count"] == 2


def test_response_representation_accepts_polymorphic_closed_and_matrix_values():
    audit = importlib.import_module("scripts.data_quality.audit")
    questions = pd.DataFrame(
        {
            "id_pergunta": ["open", "number", "choice", "check", "matrix"],
            "tipo": [
                "aberta",
                "numerica",
                "multipla_escolha",
                "caixas_de_selecao",
                "matriz_avaliacao",
            ],
        }
    )
    responses = pd.DataFrame(
        {
            "id_pergunta": [
                "open",
                "number",
                "choice",
                "choice",
                "choice",
                "check",
                "matrix",
                "matrix",
                "matrix",
                "matrix",
            ],
            "alternativa": [
                None,
                None,
                "Opção A",
                None,
                None,
                "Opção B",
                None,
                "Escala 5",
                None,
                None,
            ],
            "linha_matriz": [
                None,
                None,
                None,
                None,
                None,
                None,
                "Linha A",
                None,
                None,
                "Linha sem coluna",
            ],
            "coluna_matriz": [
                None,
                None,
                None,
                None,
                None,
                None,
                "Coluna 1",
                None,
                None,
                None,
            ],
            "valor": [
                "NA",
                0,
                None,
                "Opção serializada",
                None,
                None,
                None,
                "5",
                "5",
                None,
            ],
        }
    )

    result = audit.audit_response_representations(responses, questions)

    assert result["total_row_count"] == 10
    assert result["evaluable_row_count"] == 10
    assert result["valid_representation_count"] == 7
    assert result["missing_representation_count"] == 3
    assert result["by_question_type"]["multipla_escolha"] == {
        "row_count": 3,
        "valid_representation_count": 2,
        "missing_representation_count": 1,
        "valid_representation_pct": pytest.approx(200 / 3),
        "accepted_representation_count_by_rule": {
            "alternativa": 1,
            "valor": 1,
        },
        "accepted_representation_counts_are_non_additive": True,
    }
    assert result["by_question_type"]["matriz_avaliacao"] == {
        "row_count": 4,
        "valid_representation_count": 2,
        "missing_representation_count": 2,
        "valid_representation_pct": pytest.approx(50.0),
        "accepted_representation_count_by_rule": {
            "linha_matriz+coluna_matriz": 1,
            "alternativa+valor": 1,
        },
        "accepted_representation_counts_are_non_additive": True,
    }


def test_response_representation_reports_unknown_unsupported_and_ambiguous_types():
    audit = importlib.import_module("scripts.data_quality.audit")
    questions = pd.DataFrame(
        {
            "id_pergunta": ["known", "unsupported", "duplicate", "duplicate"],
            "tipo": ["aberta", "ranking", "aberta", "numerica"],
        }
    )
    responses = pd.DataFrame(
        {
            "id_pergunta": ["known", "unsupported", "missing", "duplicate"],
            "alternativa": [None, "A", None, None],
            "linha_matriz": [None, None, None, None],
            "coluna_matriz": [None, None, None, None],
            "valor": ["texto", None, "texto", "1"],
        }
    )

    result = audit.audit_response_representations(responses, questions)

    assert result["evaluable_row_count"] == 1
    assert result["valid_representation_count"] == 1
    assert result["unknown_question_row_count"] == 1
    assert result["unsupported_question_type_row_count"] == 1
    assert result["ambiguous_question_type_row_count"] == 1
    assert result["not_evaluable_row_count"] == 3
    assert result["question_contract"] == {
        "duplicate_question_id_count": 1,
        "ambiguous_question_id_count": 1,
    }


def test_declared_relationships_match_the_eight_observed_links():
    try:
        schema = importlib.import_module("scripts.data_quality.schema")
    except ModuleNotFoundError as exc:
        if not (
            "scripts.data_quality.schema" == exc.name
            or "scripts.data_quality.schema".startswith(f"{exc.name}.")
        ):
            raise
        pytest.skip(
            f"Contrato TDD pendente: implemente scripts.data_quality.schema ({exc}).",
        )

    relationships = {
        (item["child"], item["parent"]) for item in schema.RELATIONSHIPS
    }
    assert relationships == {
        ("clientes.id_empresa", "empresas.ID"),
        ("questoes.pesquisa_id", "pesquisas.id"),
        ("respondentes.id_pesq", "pesquisas.id"),
        ("respondentes.id_empresa", "empresas.ID"),
        ("respondentes.id_cliente", "clientes.id_cliente"),
        ("respostas.pesquisa_id", "pesquisas.id"),
        ("respostas.id_pergunta", "questoes.id_pergunta"),
        ("respostas.id_empresa", "empresas.ID"),
    }
    assert all("respondent_id" not in link for pair in relationships for link in pair)


def test_schema_declares_required_business_columns_and_logical_keys():
    try:
        schema = importlib.import_module("scripts.data_quality.schema")
    except ModuleNotFoundError as exc:
        if not (
            "scripts.data_quality.schema" == exc.name
            or "scripts.data_quality.schema".startswith(f"{exc.name}.")
        ):
            raise
        pytest.skip(
            f"Contrato TDD pendente: implemente scripts.data_quality.schema ({exc}).",
        )

    assert {name: set(columns) for name, columns in schema.REQUIRED_COLUMNS.items()} == {
        "clientes": {"id_cliente", "id_empresa", "cargo", "departamento", "e-mail"},
        "empresas": {
            "ID",
            "Nome Fantasia",
            "% de mercado",
            "Nacionalidade",
            "Associado",
            "Tipo de Associado",
            "Cidade",
            "Estado",
            "País",
        },
        "pesquisas": {
            "id",
            "titulo",
            "status",
            "tipo",
            "area",
            "participantes",
            "part_mercado",
            "data_solicitacao",
            "data_aprov",
            "data_divulgacao",
            "data_limite",
            "prorrogada_ate",
            "data_entrega",
            "dias_uteis_para_entrega",
            "complexidade",
            "tipo de resposta",
            "tempo_preenchimento",
            "objetivos",
            "dia da semana de lançamento",
            "dias úteis aberta",
            "dias entre a solicitação e a divulgação",
            "dias para tabulação",
        },
        "questoes": {
            "id_pergunta",
            "pesquisa_id",
            "pesquisa_titulo",
            "enunciado",
            "tipo",
            "qtd_alternativas",
            "alternativas",
            "linhas_matriz",
            "colunas_matriz",
            "confianca",
            "formato_arquivo",
            "col_origem",
            "observacoes",
        },
        "respondentes": {
            "id_pesq",
            "hora_inicio",
            "hora_termino",
            "id_empresa",
            "market_share",
            "id_cliente",
        },
        "respostas": {
            "id_resposta",
            "pesquisa_id",
            "id_pergunta",
            "respondent_id",
            "id_empresa",
            "alternativa",
            "linha_matriz",
            "coluna_matriz",
            "valor",
        },
    }
    assert schema.PRIMARY_KEYS == {
        "clientes": ["id_cliente"],
        "empresas": ["ID"],
        "pesquisas": ["id"],
        "questoes": ["id_pergunta"],
        "respondentes": ["id_pesq", "id_empresa", "id_cliente"],
        "respostas": ["id_resposta"],
    }
