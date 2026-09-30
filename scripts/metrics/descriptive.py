"""Estatística descritiva determinística por tipo matemático de variável."""

from __future__ import annotations

import math

import pandas as pd


def describe_numeric(series: pd.Series) -> dict:
    """Resume uma amostra numérica usando desvio-padrão amostral (ddof=1)."""
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    valid_count = len(valid)
    result = {
        "valid_observations": valid_count,
        "missing_observations": len(series) - valid_count,
        "mean": None,
        "median": None,
        "minimum": None,
        "maximum": None,
        "range": None,
        "sample_std_dev": None,
        "coefficient_of_variation_pct": None,
    }
    if valid_count == 0:
        return result

    mean = float(valid.mean())
    minimum = float(valid.min())
    maximum = float(valid.max())
    sample_std = float(valid.std(ddof=1)) if valid_count > 1 else None
    result.update(
        {
            "mean": mean,
            "median": float(valid.median()),
            "minimum": minimum,
            "maximum": maximum,
            "range": maximum - minimum,
            "sample_std_dev": sample_std,
            "coefficient_of_variation_pct": (
                sample_std / abs(mean) * 100
                if sample_std is not None and not math.isclose(mean, 0.0, abs_tol=1e-12)
                else None
            ),
        }
    )
    return result


def describe_categorical(series: pd.Series) -> dict:
    """Calcula frequência, percentual e todas as modas não nulas."""
    valid = series.dropna().astype("string").str.strip()
    valid = valid[valid.ne("")]
    valid_count = len(valid)
    counts = valid.value_counts().to_dict()
    ordered = sorted(counts.items(), key=lambda item: (-int(item[1]), str(item[0])))
    frequencies = {str(value): int(count) for value, count in ordered}
    max_count = max(frequencies.values(), default=None)
    return {
        "valid_observations": valid_count,
        "missing_observations": len(series) - valid_count,
        "frequencies": frequencies,
        "percentages": {
            value: float(count / valid_count * 100)
            for value, count in frequencies.items()
        },
        "modes": sorted(
            [value for value, count in frequencies.items() if count == max_count]
        )
        if max_count is not None
        else [],
    }


def describe_temporal(series: pd.Series, *, frequency: str = "month") -> dict:
    """Resume intervalo observado e contagem por mês, trimestre ou ano."""
    dates = pd.to_datetime(series, errors="coerce", dayfirst=True, format="mixed")
    valid = dates.dropna()
    aliases = {"month": "M", "quarter": "Q", "year": "Y"}
    if frequency not in aliases:
        raise ValueError("Frequência deve ser 'month', 'quarter' ou 'year'.")

    if valid.empty:
        distribution = {}
        minimum = maximum = None
    else:
        periods = valid.dt.to_period(aliases[frequency]).astype("string")
        distribution = {
            str(period): int(count)
            for period, count in periods.value_counts().sort_index().items()
        }
        minimum = valid.min().isoformat()
        maximum = valid.max().isoformat()
    return {
        "valid_observations": len(valid),
        "missing_or_invalid_observations": len(series) - len(valid),
        "frequency": frequency,
        "minimum": minimum,
        "maximum": maximum,
        "distribution": distribution,
    }


def detect_iqr_outliers(series: pd.Series) -> dict:
    """Sinaliza observações fora de 1,5 IQR sem removê-las."""
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    if valid.empty:
        return {
            "q1": None,
            "q3": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
            "outlier_values": [],
            "valid_observations": 0,
        }

    q1 = float(valid.quantile(0.25))
    q3 = float(valid.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = valid[(valid < lower_bound) | (valid > upper_bound)]
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": len(outliers),
        "outlier_values": [float(value) for value in outliers.tolist()],
        "valid_observations": len(valid),
    }
