"""Bloqueia dados brutos, contratos internos e padrões pessoais no site gerado."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = PROJECT_ROOT / "publication" / "privacy-policy.json"


def validate_private_site(
    site_dir: str | Path,
    policy_path: str | Path = DEFAULT_POLICY,
) -> list[str]:
    root = Path(site_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Site não encontrado: {root}")
    policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    extensions = {item.casefold() for item in policy["forbidden_file_extensions"]}
    allowed_json = {
        item.casefold() for item in policy.get("allowed_generated_json", [])
    }
    path_fragments = [item.casefold() for item in policy["forbidden_path_fragments"]]
    patterns = [re.compile(item, re.IGNORECASE) for item in policy["forbidden_text_patterns"]]
    violations: list[str] = []

    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        folded = relative.casefold()
        if path.suffix.casefold() in extensions and folded not in allowed_json:
            violations.append(f"extensão proibida: {relative}")
        if any(fragment in folded for fragment in path_fragments):
            violations.append(f"caminho proibido: {relative}")
        # Assets JS/CSS do tema podem conter metadados de terceiros; o conteúdo
        # editorial pesquisável está integralmente em HTML e no índice JSON.
        if path.suffix.casefold() in {".html", ".txt", ".xml", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in patterns:
                if pattern.search(text):
                    violations.append(
                        f"padrão proibido {pattern.pattern!r}: {relative}"
                    )

    if not (root / "index.html").is_file():
        violations.append("index.html ausente")
    if violations:
        raise ValueError("Privacy gate rejeitou o site:\n- " + "\n- ".join(violations))
    return violations


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    return parser


def main() -> int:
    args = _parser().parse_args()
    validate_private_site(args.site_dir, args.policy)
    print("Privacy gate aprovado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
