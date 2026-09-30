"""Contratos para estatística descritiva por tipo de variável."""

from __future__ import annotations

import math

import pandas as pd
import pytest


def test_numeric_statistics_use_sample_standard_deviation(descriptive_api):
    result = descriptive_api.describe_numeric(pd.Series([1.0, 2.0, 3.0, 4.0, None]))

    assert result["valid_observations"] == 4
    assert result["missing_observations"] == 1
    assert result["mean"] == pytest.approx(2.5)
    assert result["median"] == pytest.approx(2.5)
    assert result["minimum"] == pytest.approx(1.0)
    assert result["maximum"] == pytest.approx(4.0)
    assert result["range"] == pytest.approx(3.0)
    assert result["sample_std_dev"] == pytest.approx(math.sqrt(5 / 3))
    assert result["coefficient_of_variation_pct"] == pytest.approx(
        math.sqrt(5 / 3) / 2.5 * 100
    )


def test_cv_is_null_when_mean_is_zero(descriptive_api):
    result = descriptive_api.describe_numeric(pd.Series([-1.0, 1.0]))
    assert result["mean"] == pytest.approx(0.0)
    assert result["coefficient_of_variation_pct"] is None


def test_single_or_empty_samples_do_not_invent_dispersion(descriptive_api):
    single = descriptive_api.describe_numeric(pd.Series([5.0]))
    empty = descriptive_api.describe_numeric(pd.Series([None, None], dtype="float64"))

    assert single["sample_std_dev"] is None
    assert single["coefficient_of_variation_pct"] is None
    assert empty["valid_observations"] == 0
    for field in ("mean", "median", "minimum", "maximum", "range", "sample_std_dev"):
        assert empty[field] is None


def test_iqr_flags_outliers_without_removing_observations(descriptive_api):
    series = pd.Series([10, 12, 14, 15, 16, 18, 20, 22, 25, 100])
    result = descriptive_api.detect_iqr_outliers(series)

    assert result["q1"] == pytest.approx(14.25)
    assert result["q3"] == pytest.approx(21.5)
    assert result["iqr"] == pytest.approx(7.25)
    assert result["lower_bound"] == pytest.approx(3.375)
    assert result["upper_bound"] == pytest.approx(32.375)
    assert result["outlier_count"] == 1
    assert result["outlier_values"] == [100.0]
    assert result["valid_observations"] == 10


def test_categorical_statistics_report_frequency_percentage_and_all_modes(
    descriptive_api,
):
    result = descriptive_api.describe_categorical(
        pd.Series(["A", "A", "B", "B", None])
    )

    assert result["valid_observations"] == 4
    assert result["missing_observations"] == 1
    assert result["frequencies"] == {"A": 2, "B": 2}
    assert result["percentages"] == {"A": 50.0, "B": 50.0}
    assert result["modes"] == ["A", "B"]


def test_temporal_statistics_are_grouped_by_month_and_track_invalid_values(
    descriptive_api,
):
    result = descriptive_api.describe_temporal(
        pd.Series(
            [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-15"),
                pd.Timestamp("2024-02-01"),
                pd.NaT,
            ]
        ),
        frequency="month",
    )

    assert result["valid_observations"] == 3
    assert result["missing_or_invalid_observations"] == 1
    assert result["minimum"] == "2024-01-01T00:00:00"
    assert result["maximum"] == "2024-02-01T00:00:00"
    assert result["distribution"] == {"2024-01": 2, "2024-02": 1}
