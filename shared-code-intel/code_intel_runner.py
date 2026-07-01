from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


DEFAULT_ENGINE = "tree-sitter"
DEFAULT_IMAGE = "guidelines-code-intel:local"
DEFAULT_SCHEMA_VERSION = "1.0"
DEFAULT_CONFIG_PATH = Path("code-intel/config/index.yaml")
DEFAULT_INDEX_DIR = Path("code-intel/index")
DEFAULT_CACHE_DIR = Path(".code-intel-cache")
DEFAULT_CONTAINER_CACHE_DIR = "/cache/code-intel"
DEFAULT_CONTAINER_WORKDIR = "/workspace"
DEFAULT_TOOL_COMMAND = "code-intel"
DEFAULT_ARTIFACT_FILENAMES = {
    "manifest": "manifest.json",
    "files": "files.json",
    "symbols": "symbols.json",
    "edges": "edges.json",
    "chunks": "chunks.json",
}
SUPPORTED_ACTIONS = {"index", "graph", "embeddings", "query", "config"}


class DockerUnavailableError(RuntimeError):
    pass


def build_index_paths(index_root: str | Path) -> dict[str, Path]:
    root = Path(index_root)
    return {name: root / filename for name, filename in DEFAULT_ARTIFACT_FILENAMES.items()}


def normalize_changed_files(paths: list[str]) -> list[str]:
    normalized = {
        str(Path(path)).replace("\\", "/")
        for path in paths
        if str(path).strip()
    }
    return sorted(normalized)


def build_manifest(
    *,
    tool_version: str,
    commit_sha: str,
    generated_at: str,
    index_root: str | Path,
    changed_files: list[str] | None = None,
    engine: str = DEFAULT_ENGINE,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
) -> dict[str, object]:
    artifacts = {
        name: str(path).replace("\\", "/")
        for name, path in build_index_paths(index_root).items()
    }
    return {
        "schema_version": schema_version,
        "tool_version": tool_version,
        "engine": engine,
        "commit_sha": commit_sha,
        "generated_at": generated_at,
        "artifacts": artifacts,
        "changed_files": normalize_changed_files(changed_files or []),
    }


def resolve_docker_path() -> str:
    docker_path = shutil.which("docker") or shutil.which("docker.exe")
    if docker_path:
        return docker_path
    raise DockerUnavailableError(
        "Missing 'docker' in PATH. Install Docker before running code-intelligence tasks."
    )


def ensure_docker_ready(docker_path: str) -> None:
    result = subprocess.run(
        [docker_path, "info", "--format", "{{.ServerVersion}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return
    message = result.stderr.strip() or result.stdout.strip() or "unknown Docker daemon error"
    raise DockerUnavailableError(f"Docker daemon is unavailable. Start Docker and retry. Details: {message}")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing code-intel config: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid code-intel config at {path}: expected a mapping at the document root.")
    return data


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Expected a list, got {type(value).__name__}")
    return [str(item) for item in value if str(item).strip()]


def _coerce_repo_path(repo_root: Path, raw_path: str | Path) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def load_runtime_settings(
    repo_root: str | Path,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    resolved_config_path = _coerce_repo_path(root, config_path or DEFAULT_CONFIG_PATH)
    raw = _load_yaml(resolved_config_path)

    artifacts = raw.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        raise ValueError("Invalid code-intel config: artifacts must be a mapping.")

    return {
        "engine": str(raw.get("engine") or DEFAULT_ENGINE),
        "image": str(raw.get("image") or DEFAULT_IMAGE),
        "config_path": resolved_config_path,
        "index_dir": _coerce_repo_path(root, artifacts.get("index_dir", DEFAULT_INDEX_DIR)),
        "cache_dir": _coerce_repo_path(root, artifacts.get("cache_dir", DEFAULT_CACHE_DIR)),
        "languages": _string_list(raw.get("languages")),
        "include": _string_list(raw.get("include")),
        "exclude": _string_list(raw.get("exclude")),
        "incremental": bool(raw.get("incremental", True)),
    }


def build_docker_command(
    *,
    docker_path: str,
    repo_root: str | Path,
    action: str,
    settings: dict[str, Any],
    changed_files: list[str] | None = None,
    query: str | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    if action not in SUPPORTED_ACTIONS - {"config"}:
        raise ValueError(f"Unsupported code-intel action: {action}")

    root = Path(repo_root).resolve()
    repo_mount = f"{root}:/workspace"
    cache_mount = f"{Path(settings['cache_dir']).resolve()}:{DEFAULT_CONTAINER_CACHE_DIR}"

    command = [
        docker_path,
        "run",
        "--rm",
        "-v",
        repo_mount,
        "-v",
        cache_mount,
        "-w",
        DEFAULT_CONTAINER_WORKDIR,
        settings["image"],
        DEFAULT_TOOL_COMMAND,
        "--config",
        _repo_relative_path(Path(settings["config_path"]), root),
        "--index-dir",
        _repo_relative_path(Path(settings["index_dir"]), root),
        "--engine",
        str(settings["engine"]),
        action,
    ]

    for path in normalize_changed_files(changed_files or []):
        command.extend(["--changed-file", path])

    if query:
        command.extend(["--query", query])

    command.extend(list(extra_args or []))
    return command


def render_resolved_config(settings: dict[str, Any], repo_root: str | Path | None = None) -> str:
    root = Path(repo_root).resolve() if repo_root else Path(settings["config_path"]).resolve().parents[2]
    payload = {
        "engine": settings["engine"],
        "image": settings["image"],
        "config_path": _repo_relative_path(Path(settings["config_path"]), root),
        "index_dir": _repo_relative_path(Path(settings["index_dir"]), root),
        "cache_dir": _repo_relative_path(Path(settings["cache_dir"]), root),
        "languages": list(settings.get("languages") or []),
        "include": list(settings.get("include") or []),
        "exclude": list(settings.get("exclude") or []),
        "incremental": bool(settings.get("incremental", True)),
        "tools": settings.get("tools") or {},
    }
    return json.dumps(payload, indent=2, sort_keys=False)


def run_action(
    *,
    repo_root: str | Path,
    action: str,
    config_path: str | Path | None = None,
    changed_files: list[str] | None = None,
    query: str | None = None,
    extra_args: list[str] | None = None,
) -> int:
    settings = load_runtime_settings(repo_root=repo_root, config_path=config_path)
    if action == "config":
        print(render_resolved_config(settings, repo_root=repo_root))
        return 0

    docker_path = resolve_docker_path()
    ensure_docker_ready(docker_path)
    command = build_docker_command(
        docker_path=docker_path,
        repo_root=repo_root,
        action=action,
        settings=settings,
        changed_files=changed_files,
        query=query,
        extra_args=extra_args,
    )
    print(f"Running: {' '.join(command)}", flush=True)
    return subprocess.run(command, cwd=Path(repo_root), check=False).returncode


def main(
    argv: list[str],
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path | None = None,
) -> int:
    if not argv:
        raise SystemExit(
            "Usage: python code-intel.py <index|graph|embeddings|query|config> [args...]\n"
            "Examples:\n"
            "  python code-intel.py index\n"
            "  python code-intel.py graph\n"
            "  python code-intel.py query MyClass.my_method\n"
            "  python code-intel.py config"
        )

    action = argv[0]
    remainder = list(argv[1:])
    if action not in SUPPORTED_ACTIONS:
        raise SystemExit(f"Unsupported action: {action}")

    root = Path(repo_root or Path.cwd()).resolve()
    if action == "query":
        if not remainder:
            raise SystemExit("Missing query string. Use: python code-intel.py query <symbol-or-pattern>")
        return run_action(
            repo_root=root,
            action=action,
            config_path=config_path,
            query=remainder[0],
            extra_args=remainder[1:],
        )

    return run_action(
        repo_root=root,
        action=action,
        config_path=config_path,
        extra_args=remainder,
    )
