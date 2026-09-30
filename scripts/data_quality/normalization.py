"""Normalização imutável de identificadores, datas e números locais."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from scripts.data_quality.schema import (
    DATE_COLUMNS,
    IDENTIFIER_COLUMNS,
    NUMERIC_COLUMNS,
    PERCENTAGE_COLUMNS,
)


def _localized_numeric(series: pd.Series, *, percentage: bool = False) -> pd.Series:
    text = series.astype("string").str.strip()
    if percentage:
        text = text.str.replace("%", "", regex=False).str.strip()

    has_comma = text.str.contains(",", regex=False, na=False)
    normalized = text.copy()
    normalized.loc[has_comma] = (
        text.loc[has_comma]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(normalized, errors="coerce")


def _record_parsing_error(
    errors: list[dict],
    dataset: str,
    column: str,
    source: pd.Series,
    parsed: pd.Series,
) -> None:
    invalid_count = int((source.notna() & parsed.isna()).sum())
    if invalid_count:
        errors.append(
            {
                "dataset": dataset,
                "column": column,
                "invalid_count": invalid_count,
            }
        )


def _existing(columns: Iterable[str], frame: pd.DataFrame) -> Iterable[str]:
    return (column for column in columns if column in frame.columns)


def normalize_datasets(
    datasets: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    """Retorna cópias normalizadas e erros de conversão agregados."""
    normalized = {name: frame.copy(deep=True) for name, frame in datasets.items()}
    parsing_errors: list[dict] = []

    for dataset_name, frame in normalized.items():
        for column in _existing(IDENTIFIER_COLUMNS.get(dataset_name, ()), frame):
            frame[column] = frame[column].astype("string").str.strip()

        for column in _existing(PERCENTAGE_COLUMNS.get(dataset_name, ()), frame):
            source = frame[column]
            parsed = _localized_numeric(source, percentage=True)
            _record_parsing_error(
                parsing_errors, dataset_name, column, source, parsed
            )
            frame[column] = parsed

        for column in _existing(NUMERIC_COLUMNS.get(dataset_name, ()), frame):
            source = frame[column]
            parsed = _localized_numeric(source)
            _record_parsing_error(
                parsing_errors, dataset_name, column, source, parsed
            )
            frame[column] = parsed

        for column in _existing(DATE_COLUMNS.get(dataset_name, ()), frame):
            source = frame[column]
            parsed = pd.to_datetime(
                source,
                errors="coerce",
                dayfirst=True,
                format="mixed",
            )
            _record_parsing_error(
                parsing_errors, dataset_name, column, source, parsed
            )
            frame[column] = parsed

    return normalized, parsing_errors
