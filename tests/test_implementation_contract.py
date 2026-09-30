"""Guarda TDD que apresenta pendências de implementação sem ruído repetitivo."""

from __future__ import annotations

import importlib


REQUIRED_CALLABLES = {
    "scripts.data_quality.schema": [],
    "scripts.data_quality.ingestion": ["load_datasets"],
    "scripts.data_quality.normalization": ["normalize_datasets"],
    "scripts.data_quality.audit": [
        "audit_dataset",
        "audit_relationship",
        "audit_conditional_missingness",
    ],
    "scripts.metrics.descriptive": [
        "describe_numeric",
        "describe_categorical",
        "describe_temporal",
        "detect_iqr_outliers",
    ],
    "scripts.metrics.kpi_calculator": [
        "calculate_kpis",
        "compare_granularities",
    ],
    "scripts.runners.run_full_analysis": ["run_analysis"],
}


def test_required_pipeline_entry_points_are_implemented():
    missing = []

    for module_name, callable_names in REQUIRED_CALLABLES.items():
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if not (module_name == exc.name or module_name.startswith(f"{exc.name}.")):
                raise
            missing.append(f"módulo {module_name}")
            continue

        for callable_name in callable_names:
            if not callable(getattr(module, callable_name, None)):
                missing.append(f"função {module_name}.{callable_name}()")

    assert not missing, "Contratos TDD pendentes:\n- " + "\n- ".join(missing)
