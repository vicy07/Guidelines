from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ToolchainSettings:
    repo_root: Path
    config_path: Path
    primary_engine: str
    languages: list[str]
    include: list[str]
    exclude: list[str]
    incremental: bool
    tools: dict[str, dict[str, Any]]
    raw_artifacts: dict[str, Path]


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML config at {path}: expected a mapping.")
    return data


def load_toolchain_settings(repo_root: Path, config_path: Path) -> ToolchainSettings:
    raw = _read_yaml(config_path)
    index_dir = repo_root / "code-intel" / "index"
    tools = raw.get("tools") or {}
    if not isinstance(tools, dict):
        raise ValueError("tools must be a mapping")
    tools.setdefault("scip", {"enabled": True, "indexers": {}})
    tools.setdefault("ast_grep", {"enabled": True})
    tools.setdefault("ripgrep", {"enabled": True})
    tools.setdefault("fallback_tree_sitter", {"enabled": True})
    return ToolchainSettings(
        repo_root=repo_root,
        config_path=config_path,
        primary_engine=str(raw.get("engine") or "scip"),
        languages=[str(item) for item in raw.get("languages") or []],
        include=[str(item) for item in raw.get("include") or ["src"]],
        exclude=[str(item) for item in raw.get("exclude") or []],
        incremental=bool(raw.get("incremental", True)),
        tools=tools,
        raw_artifacts={
            "scip": index_dir / "scip",
            "ast_grep": index_dir / "ast-grep",
        },
    )
