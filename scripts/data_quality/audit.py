"""Métricas puras de qualidade, chaves e integridade referencial."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from scripts.data_quality.schema import RESPONSE_REPRESENTATION_RULES


def _validate_columns(
    frame: pd.DataFrame, columns: Sequence[str], dataset_name: str
) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(
            f"Base {dataset_name}: colunas não encontradas: {', '.join(missing)}"
        )


def _is_present(series: pd.Series) -> pd.Series:
    """Reconhece conteúdo material, incluindo sentinelas textuais como ``NA``."""
    return (
        series.notna()
        & series.astype("string").str.strip().ne("").fillna(False)
    )


def audit_dataset(
    frame: pd.DataFrame,
    dataset_name: str,
    primary_key: Sequence[str] | None = None,
) -> dict:
    """Calcula volumetria, completude, duplicidade, constantes e chave lógica."""
    row_count = len(frame)
    null_counts = {
        str(column): int((~_is_present(frame[column])).sum())
        for column in frame.columns
    }
    completeness = {
        str(column): (
            float((row_count - null_count) / row_count * 100)
            if row_count
            else None
        )
        for column, null_count in null_counts.items()
    }
    constant_columns = [
        str(column)
        for column in frame.columns
        if row_count > 0 and frame[column].nunique(dropna=True) <= 1
    ]

    result = {
        "dataset_name": dataset_name,
        "row_count": row_count,
        "column_count": len(frame.columns),
        "null_count_by_column": null_counts,
        "completeness_pct_by_column": completeness,
        "overall_completeness_pct": (
            float(sum(completeness.values()) / len(completeness))
            if row_count and completeness
            else None
        ),
        "duplicate_row_count": int(frame.duplicated().sum()),
        "constant_columns": constant_columns,
    }

    if primary_key is not None:
        key_columns = list(primary_key)
        _validate_columns(frame, key_columns, dataset_name)
        null_mask = pd.concat(
            [~_is_present(frame[column]) for column in key_columns], axis=1
        ).any(axis=1)
        duplicate_mask = frame.duplicated(subset=key_columns, keep=False) & ~null_mask
        null_row_count = int(null_mask.sum())
        duplicate_row_count = int(duplicate_mask.sum())
        result["primary_key"] = {
            "columns": key_columns,
            "null_row_count": null_row_count,
            "duplicate_row_count": duplicate_row_count,
            "is_unique": null_row_count == 0 and duplicate_row_count == 0,
        }
    return result


def audit_relationship(
    parent: pd.DataFrame,
    child: pd.DataFrame,
    *,
    parent_key: str,
    child_key: str,
    parent_name: str,
    child_name: str,
) -> dict:
    """Conta valores órfãos distintos e linhas filhas afetadas."""
    _validate_columns(parent, [parent_key], parent_name)
    _validate_columns(child, [child_key], child_name)

    parent_values = set(parent[parent_key].dropna().tolist())
    child_values = child[child_key]
    orphan_mask = child_values.notna() & ~child_values.isin(parent_values)
    orphan_values = sorted(
        {str(value) for value in child_values.loc[orphan_mask].tolist()}
    )
    return {
        "child": f"{child_name}.{child_key}",
        "parent": f"{parent_name}.{parent_key}",
        "orphan_value_count": len(orphan_values),
        "orphan_row_count": int(orphan_mask.sum()),
        "orphan_values_sample": orphan_values[:20],
    }


def audit_conditional_missingness(
    frame: pd.DataFrame,
    *,
    column: str,
    applicability_mask: pd.Series,
) -> dict:
    """Separa ausência bruta da ausência no subconjunto em que o campo se aplica."""
    _validate_columns(frame, [column], "dataset")
    if len(applicability_mask) != len(frame):
        raise ValueError("A máscara de aplicabilidade deve ter o mesmo tamanho da base.")

    mask = pd.Series(
        applicability_mask.array,
        index=frame.index,
        dtype="boolean",
    ).fillna(False)
    total = len(frame)
    applicable_count = int(mask.sum())
    missing_mask = ~_is_present(frame[column])
    raw_missing_count = int(missing_mask.sum())
    applicable_missing_count = int((mask & missing_mask).sum())
    return {
        "column": column,
        "total_row_count": total,
        "raw_missing_count": raw_missing_count,
        "raw_missing_pct": (
            float(raw_missing_count / total * 100) if total else None
        ),
        "applicable_row_count": applicable_count,
        "applicable_missing_count": applicable_missing_count,
        "applicable_missing_pct": (
            float(applicable_missing_count / applicable_count * 100)
            if applicable_count
            else None
        ),
    }


def audit_response_representations(
    responses: pd.DataFrame,
    questions: pd.DataFrame,
    *,
    response_question_key: str = "id_pergunta",
    question_key: str = "id_pergunta",
    question_type_column: str = "tipo",
) -> dict:
    """Audita respostas polimórficas sem confundir armazenamento com ausência.

    O resultado não contém identificadores. Questões duplicadas com o mesmo tipo
    são resolvidas de forma determinística; tipos conflitantes ficam não avaliáveis
    e são contabilizados como ambiguidade do contrato.
    """
    response_fields = sorted(
        {
            field
            for alternatives in RESPONSE_REPRESENTATION_RULES.values()
            for representation in alternatives
            for field in representation
        }
    )
    _validate_columns(
        responses,
        [response_question_key, *response_fields],
        "respostas",
    )
    _validate_columns(
        questions,
        [question_key, question_type_column],
        "questoes",
    )

    question_contract = questions[[question_key, question_type_column]].copy()
    question_contract["_normalized_type"] = (
        question_contract[question_type_column]
        .astype("string")
        .str.strip()
        .str.casefold()
    )
    question_contract = question_contract.loc[
        _is_present(question_contract[question_key])
    ]
    grouped_types = question_contract.groupby(question_key, sort=False)[
        "_normalized_type"
    ].agg(lambda values: tuple(sorted(set(values.dropna().tolist()))))
    known_question_ids = set(grouped_types.index)
    ambiguous_question_ids = {
        identifier for identifier, values in grouped_types.items() if len(values) > 1
    }
    type_by_question = {
        identifier: values[0]
        for identifier, values in grouped_types.items()
        if len(values) == 1
    }
    response_types = responses[response_question_key].map(type_by_question).astype(
        "string"
    )

    physical_missing = {
        field: int((~_is_present(responses[field])).sum())
        for field in response_fields
    }
    by_question_type: dict[str, dict] = {}
    all_valid = pd.Series(False, index=responses.index, dtype="boolean")
    evaluable = pd.Series(False, index=responses.index, dtype="boolean")

    serialized_rules = {
        question_type: [list(representation) for representation in alternatives]
        for question_type, alternatives in RESPONSE_REPRESENTATION_RULES.items()
    }
    for question_type, alternatives in RESPONSE_REPRESENTATION_RULES.items():
        type_mask = response_types.eq(question_type).fillna(False)
        type_valid = pd.Series(False, index=responses.index, dtype="boolean")
        accepted_by_rule: dict[str, int] = {}
        for representation in alternatives:
            representation_mask = pd.Series(
                True, index=responses.index, dtype="boolean"
            )
            for field in representation:
                representation_mask &= _is_present(responses[field])
            rule_name = "+".join(representation)
            accepted_by_rule[rule_name] = int(
                (type_mask & representation_mask).sum()
            )
            type_valid |= representation_mask

        valid_mask = type_mask & type_valid
        row_count = int(type_mask.sum())
        valid_count = int(valid_mask.sum())
        evaluable |= type_mask
        all_valid |= valid_mask
        by_question_type[question_type] = {
            "row_count": row_count,
            "valid_representation_count": valid_count,
            "missing_representation_count": row_count - valid_count,
            "valid_representation_pct": (
                float(valid_count / row_count * 100) if row_count else None
            ),
            "accepted_representation_count_by_rule": accepted_by_rule,
            "accepted_representation_counts_are_non_additive": True,
        }

    response_question_ids = responses[response_question_key]
    unknown_question_mask = (
        ~_is_present(response_question_ids)
        | ~response_question_ids.isin(known_question_ids)
    )
    ambiguous_question_mask = response_question_ids.isin(ambiguous_question_ids)
    unsupported_type_mask = response_types.notna() & ~response_types.isin(
        RESPONSE_REPRESENTATION_RULES
    )
    total_count = len(responses)
    evaluable_count = int(evaluable.sum())
    valid_count = int(all_valid.sum())
    return {
        "total_row_count": total_count,
        "evaluable_row_count": evaluable_count,
        "valid_representation_count": valid_count,
        "missing_representation_count": evaluable_count - valid_count,
        "valid_representation_pct": (
            float(valid_count / evaluable_count * 100) if evaluable_count else None
        ),
        "unknown_question_row_count": int(unknown_question_mask.sum()),
        "unsupported_question_type_row_count": int(unsupported_type_mask.sum()),
        "ambiguous_question_type_row_count": int(ambiguous_question_mask.sum()),
        "not_evaluable_row_count": int(
            unknown_question_mask.sum()
            + unsupported_type_mask.sum()
            + ambiguous_question_mask.sum()
        ),
        "physical_missing_count_by_column": physical_missing,
        "question_contract": {
            "duplicate_question_id_count": int(
                question_contract.loc[
                    question_contract.duplicated(question_key, keep=False),
                    question_key,
                ].nunique()
            ),
            "ambiguous_question_id_count": int(
                sum(len(values) > 1 for values in grouped_types)
            ),
        },
        "representation_rules": serialized_rules,
        "by_question_type": by_question_type,
    }
