"""Leitura validada e somente leitura das seis fontes CSV."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pandas as pd

from scripts.data_quality.schema import DATASET_FILES, REQUIRED_COLUMNS


def _resolve_source_dir(source_dir: str | Path) -> Path:
    path = Path(source_dir).expanduser()
    if not path.is_dir():
        raise FileNotFoundError(f"Diretório de fontes não encontrado: {path.name or path}")
    return path


def load_datasets(source_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Carrega as fontes obrigatórias sem inferir tipos dos identificadores."""
    source_path = _resolve_source_dir(source_dir)
    missing_files = [
        filename
        for filename in DATASET_FILES.values()
        if not (source_path / filename).is_file()
    ]
    if missing_files:
        raise FileNotFoundError(
            "Fontes obrigatórias ausentes: " + ", ".join(sorted(missing_files))
        )

    datasets: dict[str, pd.DataFrame] = {}
    for dataset_name, filename in DATASET_FILES.items():
        frame = pd.read_csv(
            source_path / filename,
            sep=";",
            encoding="utf-8-sig",
            dtype="string",
            keep_default_na=False,
            na_values=[""],
            low_memory=False,
        )
        # Espaços isolados são ausência física; sentinelas textuais preenchidas
        # (por exemplo, "NA" e "N/A") continuam sendo conteúdo do parceiro.
        whitespace_only = frame.apply(
            lambda column: column.astype("string").str.strip().eq("")
        )
        frame = frame.mask(whitespace_only)
        missing_columns = [
            column
            for column in REQUIRED_COLUMNS[dataset_name]
            if column not in frame.columns
        ]
        if missing_columns:
            raise ValueError(
                f"Base {dataset_name}: colunas obrigatórias ausentes: "
                + ", ".join(missing_columns)
            )
        datasets[dataset_name] = frame
    return datasets


def source_fingerprint(source_dir: str | Path) -> str:
    """Identifica a remessa sem registrar caminho ou conteúdo individual."""
    source_path = _resolve_source_dir(source_dir)
    digest = sha256()
    for dataset_name, filename in DATASET_FILES.items():
        path = source_path / filename
        if not path.is_file():
            raise FileNotFoundError(f"Fonte obrigatória ausente: {filename}")
        digest.update(dataset_name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
