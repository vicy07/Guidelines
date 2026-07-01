from __future__ import annotations

from pathlib import Path
from typing import Any


def run_fallback_tree_sitter_index(repo_root: Path, config: dict[str, Any], changed_files: list[str]) -> dict[str, Any]:
    raise RuntimeError(
        "Tree-sitter fallback runtime is not yet wired through fallback_tree_sitter.py. "
        "Use runtime.cli.run_index until the migration is complete."
    )
