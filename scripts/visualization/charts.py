"""Geração determinística dos gráficos agregados usados pelo relatório."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "g02-matplotlib")
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from scripts.data_quality.schema import CRITICAL_FIELDS


BLUE = "#2563EB"
LIGHT_BLUE = "#93C5FD"
NAVY = "#1E3A8A"
GREEN = "#16A34A"
AMBER = "#F59E0B"
RED = "#DC2626"
GREY = "#94A3B8"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)


def _save(figure: plt.Figure, path: Path) -> Path:
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
        metadata={"Software": "Pipeline quantitativo G02"},
    )
    plt.close(figure)
    return path


def _empty_chart(title: str, path: Path) -> Path:
    figure, axis = plt.subplots(figsize=(8, 3.5))
    axis.set_title(title, fontweight="bold")
    axis.text(0.5, 0.5, "Sem observações válidas", ha="center", va="center")
    axis.set_axis_off()
    return _save(figure, path)


def _horizontal_frequency(
    series: pd.Series,
    *,
    title: str,
    path: Path,
    color: str,
    top: int | None = None,
) -> Path:
    valid = series.dropna().astype("string").str.strip()
    valid = valid[valid.ne("")]
    counts = valid.value_counts()
    if top is not None:
        counts = counts.head(top)
    if counts.empty:
        return _empty_chart(title, path)

    counts = counts.sort_values(ascending=True)
    total = len(valid)
    figure, axis = plt.subplots(figsize=(11, max(4.8, len(counts) * 0.62)))
    bars = axis.barh(counts.index.astype(str), counts.values, color=color, alpha=0.88)
    margin = max(float(counts.max()) * 0.015, 0.2)
    for bar, count in zip(bars, counts.values, strict=True):
        axis.text(
            bar.get_width() + margin,
            bar.get_y() + bar.get_height() / 2,
            f"{int(count)} ({count / total * 100:.1f}%)",
            va="center",
            fontsize=9,
        )
    axis.set_title(title, fontweight="bold", pad=12)
    axis.set_xlabel("Frequência absoluta")
    axis.set_xlim(0, float(counts.max()) * 1.28)
    return _save(figure, path)


def _critical_completeness(quality_report: dict, path: Path) -> Path:
    labels = []
    values = []
    for reference in CRITICAL_FIELDS:
        dataset_name, column = reference.split(".", 1)
        value = quality_report["datasets"][dataset_name][
            "completeness_pct_by_column"
        ][column]
        if value is not None:
            labels.append(reference)
            values.append(float(value))
    if not values:
        return _empty_chart("Completude dos campos críticos", path)

    colors = [GREEN if value >= 95 else AMBER if value >= 80 else RED for value in values]
    figure, axis = plt.subplots(figsize=(12, 7))
    bars = axis.barh(labels[::-1], values[::-1], color=colors[::-1], alpha=0.88)
    axis.axvline(95, color=GREY, linestyle="--", linewidth=1, label="Referência: 95%")
    for bar, value in zip(bars, values[::-1], strict=True):
        axis.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}%",
            va="center",
            fontsize=9,
        )
    axis.set_xlim(0, 110)
    axis.set_xlabel("Completude (%)")
    axis.set_title("Completude dos campos críticos", fontweight="bold", pad=12)
    axis.legend(loc="lower right", fontsize=8)
    return _save(figure, path)


def _temporal_researches(pesquisas: pd.DataFrame, path: Path) -> Path:
    valid = pesquisas["data_solicitacao"].dropna()
    if valid.empty:
        return _empty_chart("Volume mensal de pesquisas", path)
    counts = valid.dt.to_period("M").astype("string").value_counts().sort_index()
    labels = counts.index.astype(str).tolist()
    positions = list(range(len(counts)))
    figure, axis = plt.subplots(figsize=(16, 6))
    axis.plot(
        positions,
        counts.values,
        color=NAVY,
        marker="o",
        markersize=4,
        linewidth=2,
    )
    axis.fill_between(positions, counts.values, color=LIGHT_BLUE, alpha=0.32)
    tick_step = max(1, len(labels) // 16)
    tick_positions = positions[::tick_step]
    axis.set_xticks(tick_positions, [labels[index] for index in tick_positions])
    axis.set_title("Volume mensal de pesquisas", fontweight="bold", pad=12)
    axis.set_xlabel("Mês de data_solicitacao")
    axis.set_ylabel("Pesquisas")
    axis.grid(axis="y", color="#E2E8F0", linewidth=0.8)
    axis.tick_params(axis="x", rotation=45)
    return _save(figure, path)


def _numeric_boxplots(pesquisas: pd.DataFrame, path: Path) -> Path:
    variables = {
        "participantes": "Participantes",
        "tempo_preenchimento": "Tempo de preenchimento (min)",
        "dias_uteis_para_entrega": "Dias úteis para entrega",
    }
    available = [
        (column, label, pd.to_numeric(pesquisas[column], errors="coerce").dropna())
        for column, label in variables.items()
        if column in pesquisas.columns
    ]
    available = [item for item in available if not item[2].empty]
    if not available:
        return _empty_chart("Distribuição e outliers das variáveis numéricas", path)

    figure, axes = plt.subplots(
        1, len(available), figsize=(6 * len(available), 6.5)
    )
    if len(available) == 1:
        axes = [axes]
    for axis, (_, label, values) in zip(axes, available, strict=True):
        q1 = float(values.quantile(0.25))
        q3 = float(values.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_count = int(((values < lower) | (values > upper)).sum())
        axis.boxplot(
            values,
            patch_artist=True,
            boxprops={"facecolor": LIGHT_BLUE, "color": BLUE},
            medianprops={"color": BLUE, "linewidth": 2},
            whiskerprops={"color": BLUE},
            capprops={"color": BLUE},
            flierprops={
                "marker": "o",
                "markerfacecolor": RED,
                "markeredgecolor": RED,
                "alpha": 0.45,
                "markersize": 4,
            },
        )
        axis.set_title(
            f"{label}\nN={len(values)} · outliers IQR={outlier_count}",
            fontsize=11,
        )
        axis.set_xticks([])
        axis.set_ylabel(label)
    figure.suptitle(
        "Distribuição e outliers das variáveis numéricas",
        fontsize=12,
        fontweight="bold",
    )
    return _save(figure, path)


def generate_charts(
    datasets: dict[str, pd.DataFrame], quality_report: dict, output_dir: str | Path
) -> list[Path]:
    """Gera os sete PNGs agregados consumidos pelo relatório quantitativo."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    pesquisas = datasets["pesquisas"]
    return [
        _critical_completeness(
            quality_report, destination / "completude_variaveis_criticas.png"
        ),
        _horizontal_frequency(
            pesquisas["status"],
            title="Status das pesquisas",
            path=destination / "status_pesquisas.png",
            color=BLUE,
        ),
        _horizontal_frequency(
            pesquisas["tipo"],
            title="Tipos de pesquisa",
            path=destination / "tipo_pesquisas.png",
            color=LIGHT_BLUE,
        ),
        _horizontal_frequency(
            datasets["clientes"]["departamento"],
            title="Oito departamentos mais frequentes",
            path=destination / "departamentos_top8.png",
            color=BLUE,
            top=8,
        ),
        _horizontal_frequency(
            datasets["questoes"]["tipo"],
            title="Tipos de questão",
            path=destination / "tipo_questoes.png",
            color=LIGHT_BLUE,
        ),
        _temporal_researches(
            pesquisas, destination / "serie_temporal_pesquisas.png"
        ),
        _numeric_boxplots(pesquisas, destination / "outliers_combined.png"),
    ]
