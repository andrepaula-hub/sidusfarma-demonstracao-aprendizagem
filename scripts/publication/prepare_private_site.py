"""Constrói a origem privada do MkDocs a partir de uma allowlist fechada."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = PROJECT_ROOT / "publication" / "private-allowlist.json"
DEFAULT_DESTINATION = PROJECT_ROOT / ".build" / "private-docs"
REPORT_SOURCE = (PROJECT_ROOT / "docs" / "modelagem_quantitativa_de_dados_do_parceiro.md").resolve()
ASSET_SOURCE_ROOTS = tuple(
    (PROJECT_ROOT / "docs" / directory).resolve()
    for directory in ("images", "javascripts", "stylesheets")
)


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_destination(destination: Path) -> Path:
    resolved = destination.resolve()
    build_root = (PROJECT_ROOT / ".build").resolve()
    if resolved == build_root or not _inside(resolved, build_root):
        raise ValueError("O destino de publicação deve ser um subdiretório de .build.")
    return resolved


def _remove_readonly(function, path, _error) -> None:
    """Permite reconstrução idempotente no Windows quando um asset é read-only."""
    os.chmod(path, stat.S_IWRITE)
    function(path)


def _strip_internal_data_links(markdown: str) -> str:
    pattern = re.compile(r"\[(`?(?:quality_report|kpis_summary)\.json`?)\]\(data/[^)]+\)")
    return pattern.sub(r"\1 (contrato interno não publicado no site)", markdown)


def prepare_private_site(
    manifest_path: str | Path = DEFAULT_MANIFEST,
    destination: str | Path = DEFAULT_DESTINATION,
) -> list[Path]:
    manifest_file = Path(manifest_path).resolve()
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    target_root = _safe_destination(Path(destination))

    if target_root.exists():
        shutil.rmtree(target_root, onexc=_remove_readonly)
    target_root.mkdir(parents=True)

    copied: list[Path] = []
    for item in manifest["files"]:
        source = (PROJECT_ROOT / item["source"]).resolve()
        target = (target_root / item["destination"]).resolve()
        source_is_allowed = source == REPORT_SOURCE or any(
            _inside(source, root) for root in ASSET_SOURCE_ROOTS
        )
        if not source_is_allowed:
            raise ValueError("Fonte fora das áreas permitidas para publicação.")
        if not _inside(target, target_root):
            raise ValueError("A allowlist não pode escrever fora do destino.")
        if not source.is_file():
            raise FileNotFoundError(f"Arquivo permitido ausente: {item['source']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if item.get("transform") == "strip_internal_data_links":
            content = source.read_text(encoding="utf-8")
            target.write_text(
                _strip_internal_data_links(content), encoding="utf-8", newline="\n"
            )
        elif item.get("transform"):
            raise ValueError(f"Transformação desconhecida: {item['transform']}")
        else:
            shutil.copy2(source, target)
        copied.append(target)

    index = target_root / "index.md"
    index.write_text(
        "# Modelagem quantitativa — acesso restrito\n\n"
        "Este pacote contém somente resultados agregados aprovados para membros "
        "autenticados do projeto. Dados brutos e contratos internos não são "
        "incluídos.\n\n"
        "[Abrir o relatório quantitativo](modelagem_quantitativa_de_dados_do_parceiro.md)\n",
        encoding="utf-8",
        newline="\n",
    )
    copied.append(index)
    return copied


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    return parser


def main() -> int:
    args = _parser().parse_args()
    files = prepare_private_site(args.manifest, args.destination)
    print(f"Origem privada preparada: {len(files)} arquivos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
