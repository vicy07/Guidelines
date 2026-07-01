from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("code-intel/config/index.yaml")
DEFAULT_INDEX_DIR = Path("code-intel/index")
DEFAULT_ENGINE = "tree-sitter"
DEFAULT_TOOL_VERSION = "0.1.0"
LANGUAGE_EXTENSIONS = {
    "python": {".py"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts"},
    "tsx": {".tsx"},
    "json": {".json"},
}
SYMBOL_KINDS = {
    "python": {
        "function_definition": "function",
        "class_definition": "class",
    },
    "javascript": {
        "function_declaration": "function",
        "class_declaration": "class",
        "method_definition": "method",
    },
    "typescript": {
        "function_declaration": "function",
        "class_declaration": "class",
        "method_definition": "method",
        "interface_declaration": "interface",
    },
    "tsx": {
        "function_declaration": "function",
        "class_declaration": "class",
        "method_definition": "method",
        "interface_declaration": "interface",
    },
}
AST_GREP_PATTERNS = {
    "python": [
        "def $NAME($$$ARGS): $$$BODY",
        "class $NAME: $$$BODY",
    ],
    "javascript": [
        "function $NAME($$$ARGS) { $$$BODY }",
        "class $NAME { $$$BODY }",
        "$NAME($$$ARGS) { $$$BODY }",
    ],
    "typescript": [
        "function $NAME($$$ARGS) { $$$BODY }",
        "class $NAME { $$$BODY }",
        "interface $NAME { $$$BODY }",
        "$NAME($$$ARGS) { $$$BODY }",
    ],
    "tsx": [
        "function $NAME($$$ARGS) { $$$BODY }",
        "class $NAME { $$$BODY }",
        "interface $NAME { $$$BODY }",
        "$NAME($$$ARGS) { $$$BODY }",
    ],
}


def render_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML config at {path}: expected a mapping.")
    return data


def build_artifact_paths(index_dir: Path) -> dict[str, Path]:
    return {
        "manifest": index_dir / "manifest.json",
        "files": index_dir / "files.json",
        "symbols": index_dir / "symbols.json",
        "edges": index_dir / "edges.json",
        "chunks": index_dir / "chunks.json",
    }


def load_index_config(repo_root: Path, config_path: Path) -> dict[str, Any]:
    raw = read_yaml(config_path)
    artifacts = raw.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        raise ValueError("Invalid code-intel config: artifacts must be a mapping.")

    index_dir = repo_root / Path(str(artifacts.get("index_dir") or DEFAULT_INDEX_DIR))
    tools = raw.get("tools") or {}
    if not isinstance(tools, dict):
        raise ValueError("Invalid code-intel config: tools must be a mapping.")

    return {
        "engine": str(raw.get("engine") or DEFAULT_ENGINE),
        "languages": [str(item) for item in raw.get("languages") or []],
        "include": [str(item) for item in raw.get("include") or ["src"]],
        "exclude": [str(item) for item in raw.get("exclude") or []],
        "incremental": bool(raw.get("incremental", True)),
        "index_dir": index_dir,
        "artifacts": build_artifact_paths(index_dir),
        "image": str(raw.get("image") or ""),
        "tools": tools,
        "raw_artifacts": {
            "scip": index_dir / "scip",
            "ast_grep": index_dir / "ast-grep",
        },
    }


def _load_runtime_module(module_filename: str, module_name: str):
    module_path = Path(__file__).resolve().parent / module_filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load runtime module: {module_filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_language_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if suffix in extensions:
            return language
    return ""


def _matches_language_filters(language: str, configured_languages: list[str]) -> bool:
    if not configured_languages:
        return bool(language)
    return language in set(configured_languages)


def collect_source_files(repo_root: Path, config: dict[str, Any], changed_files: list[str]) -> list[Path]:
    allowed_languages = list(config.get("languages") or [])
    includes = [repo_root / Path(item) for item in config.get("include") or ["src"]]
    exclude_prefixes = {str(Path(item)).replace("\\", "/").rstrip("/") for item in config.get("exclude") or []}

    if changed_files:
        candidates = [repo_root / Path(item) for item in changed_files]
    else:
        candidates = []
        for include_root in includes:
            if include_root.is_file():
                candidates.append(include_root)
                continue
            if not include_root.exists():
                continue
            for path in include_root.rglob("*"):
                if path.is_file():
                    candidates.append(path)

    filtered: list[Path] = []
    seen: set[Path] = set()
    for path in sorted(candidates):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not resolved.is_file():
            continue
        relative = str(resolved.relative_to(repo_root.resolve())).replace("\\", "/")
        if any(relative == prefix or relative.startswith(f"{prefix}/") for prefix in exclude_prefixes):
            continue
        language = resolve_language_for_path(resolved)
        if not _matches_language_filters(language, allowed_languages):
            continue
        filtered.append(resolved)
    return filtered


def _load_tree_sitter_language(language_name: str):
    from tree_sitter import Language

    if language_name == "python":
        import tree_sitter_python

        return Language(tree_sitter_python.language())
    if language_name == "javascript":
        import tree_sitter_javascript

        return Language(tree_sitter_javascript.language())
    if language_name == "typescript":
        import tree_sitter_typescript

        return Language(tree_sitter_typescript.language_typescript())
    if language_name == "tsx":
        import tree_sitter_typescript

        return Language(tree_sitter_typescript.language_tsx())
    if language_name == "json":
        import tree_sitter_json

        return Language(tree_sitter_json.language())
    raise ValueError(f"Unsupported language for runtime parsing: {language_name}")


def _make_parser(language_name: str):
    from tree_sitter import Parser

    language = _load_tree_sitter_language(language_name)
    return Parser(language)


def _node_text(source_bytes: bytes, node) -> str:
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _symbol_name(node, source_bytes: bytes) -> str:
    name_node = node.child_by_field_name("name")
    if name_node is not None:
        return _node_text(source_bytes, name_node).strip()
    for child in node.children:
        if child.type == "identifier":
            return _node_text(source_bytes, child).strip()
    return ""


def resolve_symbol_kind(language_name: str, node_type: str, parent_kind: str) -> str:
    if language_name == "python" and node_type == "function_definition" and parent_kind == "class":
        return "method"
    return SYMBOL_KINDS.get(language_name, {}).get(node_type, "")


def _call_name(node, source_bytes: bytes) -> str:
    function_node = node.child_by_field_name("function")
    if function_node is None:
        return ""
    return _node_text(source_bytes, function_node).strip()


def _parse_call_reference(raw_name: str) -> tuple[str, str]:
    value = raw_name.strip()
    if not value:
        return "", ""
    parts = [part.strip() for part in value.split(".") if part.strip()]
    if len(parts) == 1:
        return "", parts[0]
    return ".".join(parts[:-1]), parts[-1]


def _extract_python_import_targets(node_text: str) -> dict[str, str]:
    text = node_text.strip()
    targets: dict[str, str] = {}
    if text.startswith("import "):
        raw_items = text[len("import ") :].split(",")
        for raw_item in raw_items:
            item = raw_item.strip()
            if not item:
                continue
            base, _, alias = item.partition(" as ")
            module_name = base.strip()
            local_name = (alias or module_name.split(".", 1)[0]).strip()
            targets[local_name] = f"external:import:{module_name}"
        return targets

    if text.startswith("from ") and " import " in text:
        source_module, imported = text[len("from ") :].split(" import ", 1)
        for raw_item in imported.split(","):
            item = raw_item.strip()
            if not item:
                continue
            base, _, alias = item.partition(" as ")
            imported_name = base.strip()
            local_name = (alias or imported_name).strip()
            targets[local_name] = f"external:import:{source_module.strip()}.{imported_name}"
    return targets


def _extract_typescript_import_targets(node_text: str) -> dict[str, str]:
    text = node_text.strip().rstrip(";")
    if not text.startswith("import "):
        return {}
    if " from " not in text:
        module_name = text[len("import ") :].strip().strip("'\"")
        return {module_name: f"external:import:{module_name}"} if module_name else {}

    clause, module_name = text[len("import ") :].split(" from ", 1)
    module_name = module_name.strip().strip("'\"")
    clause = clause.strip()
    targets: dict[str, str] = {}

    if clause.startswith("{") and clause.endswith("}"):
        for raw_item in clause[1:-1].split(","):
            item = raw_item.strip()
            if not item:
                continue
            imported_name, _, alias = item.partition(" as ")
            exported_name = imported_name.strip()
            local_name = (alias or exported_name).strip()
            targets[local_name] = f"external:import:{module_name}.{exported_name}"
        return targets

    if clause.startswith("* as "):
        local_name = clause[len("* as ") :].strip()
        if local_name:
            targets[local_name] = f"external:import:{module_name}"
        return targets

    local_name = clause.strip()
    if local_name:
        targets[local_name] = f"external:import:{module_name}.default"
    return targets


def extract_import_targets(language_name: str, node_text: str) -> dict[str, str]:
    if language_name == "python":
        return _extract_python_import_targets(node_text)
    if language_name in {"javascript", "typescript", "tsx"}:
        return _extract_typescript_import_targets(node_text)
    return {}


def build_resolved_edges(
    *,
    file_path: str,
    symbols: list[dict[str, Any]],
    import_targets: dict[str, str],
    pending_calls: list[dict[str, str]],
) -> list[dict[str, Any]]:
    module_symbol = next((item for item in symbols if item["kind"] == "module"), None)
    if module_symbol is None:
        return []

    module_id = str(module_symbol["id"])
    symbols_by_id = {str(item["id"]): item for item in symbols}
    module_level_by_name = {
        str(item["name"]): str(item["id"])
        for item in symbols
        if str(item["parent_id"]) == module_id and item["kind"] != "module"
    }
    methods_by_class: dict[str, dict[str, str]] = {}
    for item in symbols:
        if item["kind"] != "method":
            continue
        parent_id = str(item["parent_id"])
        methods_by_class.setdefault(parent_id, {})[str(item["name"])] = str(item["id"])

    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()

    def add_edge(source_id: str, target_id: str, kind: str) -> None:
        key = (source_id, target_id, kind, file_path)
        if key in seen:
            return
        seen.add(key)
        edges.append(
            {
                "source_id": source_id,
                "target_id": target_id,
                "kind": kind,
                "file": file_path,
            }
        )

    for item in symbols:
        parent_id = str(item.get("parent_id") or "")
        if parent_id:
            add_edge(parent_id, str(item["id"]), "contain")

    for target_id in sorted(set(import_targets.values())):
        add_edge(module_id, target_id, "import")

    for call in pending_calls:
        source_id = str(call["source_id"])
        qualifier = str(call.get("qualifier") or "")
        target_name = str(call.get("target_name") or "")
        raw_name = str(call.get("raw_name") or target_name)
        source_symbol = symbols_by_id.get(source_id, {})
        source_parent_id = str(source_symbol.get("parent_id") or "")
        resolved_target = ""

        if qualifier in {"self", "cls"} and source_parent_id in methods_by_class:
            resolved_target = methods_by_class[source_parent_id].get(target_name, "")
        elif qualifier:
            qualifier_head = qualifier.split(".", 1)[0]
            imported_target = import_targets.get(qualifier_head, "")
            if imported_target:
                suffix = raw_name[len(qualifier_head) :]
                resolved_target = f"{imported_target}{suffix}"
        else:
            resolved_target = module_level_by_name.get(target_name, "") or import_targets.get(target_name, "")

        if not resolved_target:
            resolved_target = f"external:{raw_name}"
        add_edge(source_id, resolved_target, "call")

    edges.sort(key=lambda item: (item["file"], item["source_id"], item["target_id"], item["kind"]))
    return edges


def _python_module_candidates(file_path: str) -> list[str]:
    path = Path(file_path)
    if path.suffix != ".py":
        return []
    parts = list(path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    candidates: list[str] = []
    for offset in range(len(parts)):
        candidate_parts = parts[offset:]
        if candidate_parts:
            candidates.append(".".join(candidate_parts))
    return candidates


def _typescript_resolve_relative_file(source_file: str, module_spec: str, available_files: set[str]) -> str:
    base_dir = Path(source_file).parent
    raw_target = (base_dir / module_spec).as_posix()
    candidates = []
    target_path = Path(raw_target)
    if target_path.suffix:
        candidates.append(target_path.as_posix())
    else:
        for suffix in [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json"]:
            candidates.append(target_path.with_suffix(suffix).as_posix())
        for suffix in [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json"]:
            candidates.append((target_path / f"index{suffix}").as_posix())
    for candidate in candidates:
        normalized = str(Path(candidate)).replace("\\", "/")
        if normalized in available_files:
            return normalized
    return ""


def _split_import_target(target_id: str) -> str:
    prefix = "external:import:"
    if not target_id.startswith(prefix):
        return ""
    return target_id[len(prefix) :]


def _resolve_python_import_target(
    source_file: str,
    import_spec: str,
    python_modules_to_files: dict[str, str],
    module_symbols_by_file: dict[str, str],
    module_level_symbols_by_file: dict[str, dict[str, str]],
) -> str:
    del source_file
    parts = [item for item in import_spec.split(".") if item]
    for prefix_len in range(len(parts), 0, -1):
        module_name = ".".join(parts[:prefix_len])
        target_file = python_modules_to_files.get(module_name, "")
        if not target_file:
            continue
        if prefix_len == len(parts):
            return module_symbols_by_file.get(target_file, "")
        exported_symbols = module_level_symbols_by_file.get(target_file, {})
        symbol_name = parts[prefix_len]
        return exported_symbols.get(symbol_name, "")
    return ""


def _resolve_typescript_import_target(
    source_file: str,
    import_spec: str,
    available_files: set[str],
    module_symbols_by_file: dict[str, str],
    module_level_symbols_by_file: dict[str, dict[str, str]],
) -> str:
    if import_spec.startswith("./") or import_spec.startswith("../"):
        module_spec, symbol_name = import_spec, ""
        if "." in import_spec:
            maybe_module, maybe_symbol = import_spec.rsplit(".", 1)
            if maybe_symbol.isidentifier():
                module_spec, symbol_name = maybe_module, maybe_symbol
        target_file = _typescript_resolve_relative_file(source_file, module_spec, available_files)
        if not target_file:
            return ""
        if not symbol_name:
            return module_symbols_by_file.get(target_file, "")
        return module_level_symbols_by_file.get(target_file, {}).get(symbol_name, "")
    return ""


def rewrite_cross_file_edges(
    *,
    files: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    file_languages = {str(item["path"]): str(item["language"]) for item in files}
    available_files = set(file_languages)
    module_symbols_by_file = {
        str(item["file"]): str(item["id"])
        for item in symbols
        if item["kind"] == "module"
    }
    module_level_symbols_by_file: dict[str, dict[str, str]] = {}
    for item in symbols:
        if item["kind"] == "module":
            continue
        file_path = str(item["file"])
        module_id = module_symbols_by_file.get(file_path, "")
        if str(item.get("parent_id") or "") != module_id:
            continue
        module_level_symbols_by_file.setdefault(file_path, {})[str(item["name"])] = str(item["id"])

    python_modules_to_files: dict[str, str] = {}
    for file_path, language in file_languages.items():
        if language != "python":
            continue
        for candidate in _python_module_candidates(file_path):
            python_modules_to_files.setdefault(candidate, file_path)

    rewritten: list[dict[str, Any]] = []
    for edge in edges:
        target_id = str(edge["target_id"])
        import_spec = _split_import_target(target_id)
        if not import_spec:
            rewritten.append(edge)
            continue

        source_file = str(edge["file"])
        language = file_languages.get(source_file, "")
        resolved_target = ""
        if language == "python":
            resolved_target = _resolve_python_import_target(
                source_file,
                import_spec,
                python_modules_to_files,
                module_symbols_by_file,
                module_level_symbols_by_file,
            )
        elif language in {"javascript", "typescript", "tsx"}:
            resolved_target = _resolve_typescript_import_target(
                source_file,
                import_spec,
                available_files,
                module_symbols_by_file,
                module_level_symbols_by_file,
            )

        rewritten.append({**edge, "target_id": resolved_target or target_id})

    rewritten.sort(key=lambda item: (item["file"], item["source_id"], item["target_id"], item["kind"]))
    return rewritten


def select_primary_runtime(settings: dict[str, Any]) -> str:
    tools = settings.get("tools") or {}
    scip = tools.get("scip") or {}
    languages = settings.get("languages") or []
    indexers = scip.get("indexers") or {}
    if scip.get("enabled") and languages and all(language in indexers for language in languages):
        return "scip"
    if (tools.get("fallback_tree_sitter") or {}).get("enabled"):
        return "fallback_tree_sitter"
    return "ast_grep"


def _build_symbol_id(language: str, relative_path: str, name: str, start_row: int) -> str:
    return f"{language}:{relative_path}:{name}:{start_row + 1}"


def parse_source_file(repo_root: Path, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    language_name = resolve_language_for_path(path)
    source_bytes = path.read_bytes()
    relative_path = str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")

    parser = _make_parser(language_name)
    tree = parser.parse(source_bytes)
    root = tree.root_node

    module_symbol_id = _build_symbol_id(language_name, relative_path, "<module>", 0)
    symbols = [
        {
            "id": module_symbol_id,
            "name": "<module>",
            "kind": "module",
            "language": language_name,
            "file": relative_path,
            "parent_id": "",
            "start_point": {"row": 0, "column": 0},
            "end_point": {"row": root.end_point[0], "column": root.end_point[1]},
        }
    ]
    import_targets: dict[str, str] = {}
    pending_calls: list[dict[str, str]] = []
    chunks: list[dict[str, Any]] = []

    def walk(node, current_symbol_id: str, current_symbol_kind: str) -> None:
        active_symbol_id = current_symbol_id
        active_symbol_kind = current_symbol_kind
        if node.type in {"import_statement", "import_from_statement"}:
            import_targets.update(extract_import_targets(language_name, _node_text(source_bytes, node)))
        kind = resolve_symbol_kind(language_name, node.type, current_symbol_kind)
        if kind:
            name = _symbol_name(node, source_bytes)
            if name:
                symbol_id = _build_symbol_id(language_name, relative_path, name, node.start_point[0])
                symbols.append(
                    {
                        "id": symbol_id,
                        "name": name,
                        "kind": kind,
                        "language": language_name,
                        "file": relative_path,
                        "parent_id": current_symbol_id,
                        "start_point": {"row": node.start_point[0], "column": node.start_point[1]},
                        "end_point": {"row": node.end_point[0], "column": node.end_point[1]},
                    }
                )
                chunks.append(
                    {
                        "id": f"chunk:{symbol_id}",
                        "symbol_id": symbol_id,
                        "file": relative_path,
                        "language": language_name,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "text": _node_text(source_bytes, node),
                        "embedding": None,
                    }
                )
                active_symbol_id = symbol_id
                active_symbol_kind = kind

        if node.type in {"call", "call_expression"}:
            raw_name = _call_name(node, source_bytes)
            qualifier, target_name = _parse_call_reference(raw_name)
            if target_name and active_symbol_id:
                pending_calls.append(
                    {
                        "source_id": active_symbol_id,
                        "qualifier": qualifier,
                        "target_name": target_name,
                        "raw_name": raw_name,
                    }
                )

        for child in node.children:
            if child.is_named:
                walk(child, active_symbol_id, active_symbol_kind)

    walk(root, module_symbol_id, "module")
    edges = build_resolved_edges(
        file_path=relative_path,
        symbols=symbols,
        import_targets=import_targets,
        pending_calls=pending_calls,
    )

    file_record = {
        "path": relative_path,
        "language": language_name,
        "sha256": hashlib.sha256(source_bytes).hexdigest(),
        "bytes": len(source_bytes),
        "symbol_count": len(symbols),
        "status": "indexed",
    }
    return file_record, symbols, edges, chunks


def build_query_results(query: str, symbols: list[dict[str, Any]], files: list[dict[str, Any]]) -> dict[str, Any]:
    needle = query.lower()
    return {
        "query": query,
        "symbols": [
            item
            for item in symbols
            if needle in str(item.get("name", "")).lower() or needle in str(item.get("id", "")).lower()
        ],
        "files": [
            item
            for item in files
            if needle in str(item.get("path", "")).lower()
        ],
    }


def _git_commit_sha(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return os.getenv("CODE_INTEL_COMMIT_SHA", "unknown")
    if result.returncode == 0:
        return result.stdout.strip()
    return os.getenv("CODE_INTEL_COMMIT_SHA", "unknown")


def _build_manifest(repo_root: Path, config: dict[str, Any], files: list[dict[str, Any]], symbols: list[dict[str, Any]], edges: list[dict[str, Any]], chunks: list[dict[str, Any]], changed_files: list[str]) -> dict[str, Any]:
    artifact_paths = {
        key: str(path.name)
        for key, path in config["artifacts"].items()
    }
    return {
        "schema_version": "1.0",
        "tool_version": DEFAULT_TOOL_VERSION,
        "engine": config["engine"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit_sha": _git_commit_sha(repo_root),
        "artifacts": artifact_paths,
        "counts": {
            "files": len(files),
            "symbols": len(symbols),
            "edges": len(edges),
            "chunks": len(chunks),
        },
        "changed_files": sorted(changed_files),
    }


def _write_artifacts(config: dict[str, Any], payloads: dict[str, Any]) -> None:
    config["index_dir"].mkdir(parents=True, exist_ok=True)
    for key, payload in payloads.items():
        config["artifacts"][key].write_text(render_json(payload), encoding="utf-8")


def build_chunks_from_ast_matches(symbols: list[dict[str, Any]], ast_matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    symbols_by_file: dict[str, list[dict[str, Any]]] = {}
    for item in symbols:
        if item["kind"] == "module":
            continue
        symbols_by_file.setdefault(str(item["file"]), []).append(item)

    def resolve_symbol(file_path: str, start_line: int, end_line: int) -> dict[str, Any] | None:
        candidates: list[tuple[int, str, dict[str, Any]]] = []
        for symbol in symbols_by_file.get(file_path, []):
            symbol_start = int(symbol["start_point"]["row"]) + 1
            symbol_end = int(symbol["end_point"]["row"]) + 1
            if symbol_start <= start_line and symbol_end >= end_line:
                candidates.append((symbol_end - symbol_start, str(symbol["id"]), symbol))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2]

    chunks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in ast_matches:
        file_path = str(match["file"])
        start_line = int(match["range"]["start"]["line"])
        end_line = int(match["range"]["end"]["line"])
        symbol = resolve_symbol(file_path, start_line, end_line)
        if symbol is None:
            continue
        chunk_id = f"chunk:{symbol['id']}"
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        chunks.append(
            {
                "id": chunk_id,
                "symbol_id": symbol["id"],
                "file": file_path,
                "language": symbol["language"],
                "start_line": start_line,
                "end_line": end_line,
                "text": str(match["text"]),
                "embedding": None,
            }
        )
    chunks.sort(key=lambda item: (item["file"], item["start_line"], item["end_line"], item["id"]))
    return chunks


def build_chunks_from_symbols(symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks = [
        {
            "id": f"chunk:{item['id']}",
            "symbol_id": item["id"],
            "file": item["file"],
            "language": item["language"],
            "start_line": item["start_point"]["row"] + 1,
            "end_line": item["end_point"]["row"] + 1,
            "text": "",
            "embedding": None,
        }
        for item in symbols
        if item["kind"] != "module"
    ]
    chunks.sort(key=lambda item: (item["file"], item["start_line"], item["end_line"], item["id"]))
    return chunks


def collect_ast_grep_matches(
    repo_root: Path,
    config: dict[str, Any],
    files: list[dict[str, Any]],
    ast_grep_adapter,
) -> list[dict[str, Any]]:
    if not ((config.get("tools") or {}).get("ast_grep") or {}).get("enabled"):
        return []

    indexed_files = {str(item["path"]) for item in files}
    matches: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int, str]] = set()
    for language in sorted({str(item["language"]) for item in files if str(item.get("language") or "") in AST_GREP_PATTERNS}):
        for pattern in AST_GREP_PATTERNS[language]:
            for match in ast_grep_adapter.run_ast_grep_scan(repo_root=repo_root, pattern=pattern, language=language):
                file_path = str(match.get("file") or "").replace("\\", "/")
                if file_path not in indexed_files:
                    continue
                range_payload = match.get("range") or {}
                start_line = int((range_payload.get("start") or {}).get("line", 0))
                end_line = int((range_payload.get("end") or {}).get("line", 0))
                key = (file_path, start_line, end_line, str(match.get("text") or ""))
                if key in seen:
                    continue
                seen.add(key)
                matches.append(
                    {
                        "text": str(match.get("text") or ""),
                        "range": {
                            "start": {
                                "line": start_line,
                                "column": int((range_payload.get("start") or {}).get("column", 0)),
                            },
                            "end": {
                                "line": end_line,
                                "column": int((range_payload.get("end") or {}).get("column", 0)),
                            },
                        },
                        "file": file_path,
                    }
                )
    matches.sort(key=lambda item: (item["file"], item["range"]["start"]["line"], item["range"]["end"]["line"], item["text"]))
    return matches


def merge_chunks(primary_chunks: list[dict[str, Any]], fallback_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {str(item["id"]): item for item in fallback_chunks}
    for chunk in primary_chunks:
        merged[str(chunk["id"])] = chunk
    items = list(merged.values())
    items.sort(key=lambda item: (item["file"], item["start_line"], item["end_line"], item["id"]))
    return items


def run_fallback_tree_sitter_index(repo_root: Path, config: dict[str, Any], changed_files: list[str]) -> dict[str, Any]:
    file_paths = collect_source_files(repo_root=repo_root, config=config, changed_files=changed_files)

    files: list[dict[str, Any]] = []
    symbols: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    for path in file_paths:
        file_record, file_symbols, file_edges, file_chunks = parse_source_file(repo_root, path)
        files.append(file_record)
        symbols.extend(file_symbols)
        edges.extend(file_edges)
        chunks.extend(file_chunks)

    files.sort(key=lambda item: item["path"])
    symbols.sort(key=lambda item: item["id"])
    edges.sort(key=lambda item: (item["file"], item["source_id"], item["target_id"], item["kind"]))
    chunks.sort(key=lambda item: item["id"])

    edges = rewrite_cross_file_edges(files=files, symbols=symbols, edges=edges)

    manifest = _build_manifest(repo_root, config, files, symbols, edges, chunks, changed_files)
    payloads = {
        "manifest": manifest,
        "files": files,
        "symbols": symbols,
        "edges": edges,
        "chunks": chunks,
    }
    _write_artifacts(config, payloads)
    return manifest


def run_index(repo_root: Path, config: dict[str, Any], changed_files: list[str]) -> dict[str, Any]:
    runtime = select_primary_runtime(config)
    if runtime == "fallback_tree_sitter":
        return run_fallback_tree_sitter_index(repo_root, config, changed_files)

    if runtime == "scip":
        scip_adapter = _load_runtime_module("scip_adapter.py", "shared_code_intel_scip_adapter")
        raw_scip_path = config["raw_artifacts"]["scip"] / "index.scip"
        raw_scip_path.parent.mkdir(parents=True, exist_ok=True)
        language = (config.get("languages") or [""])[0]
        command = str((((config.get("tools") or {}).get("scip") or {}).get("indexers") or {}).get(language, "")).strip()
        if command:
            status = scip_adapter.run_scip_index(command=command, repo_root=repo_root, output_path=raw_scip_path)
            if status != 0:
                raise SystemExit(status)
        scip_payload = scip_adapter.load_scip_json(output_path=raw_scip_path, repo_root=repo_root)
        files, symbols, edges = scip_adapter.normalize_scip_output(payload=scip_payload, repo_root=repo_root)
        ast_matches: list[dict[str, Any]] = []
        if ((config.get("tools") or {}).get("ast_grep") or {}).get("enabled"):
            ast_grep_adapter = _load_runtime_module("ast_grep_adapter.py", "shared_code_intel_ast_grep_adapter")
            ast_matches = collect_ast_grep_matches(
                repo_root=repo_root,
                config=config,
                files=files,
                ast_grep_adapter=ast_grep_adapter,
            )
            raw_ast_path = config["raw_artifacts"]["ast_grep"] / "matches.json"
            raw_ast_path.parent.mkdir(parents=True, exist_ok=True)
            raw_ast_path.write_text(render_json(ast_matches), encoding="utf-8")
        chunks = merge_chunks(
            build_chunks_from_ast_matches(symbols=symbols, ast_matches=ast_matches),
            build_chunks_from_symbols(symbols),
        )
        manifest = _build_manifest(repo_root, config, files, symbols, edges, chunks, changed_files)
        payloads = {
            "manifest": manifest,
            "files": files,
            "symbols": symbols,
            "edges": edges,
            "chunks": chunks,
        }
        _write_artifacts(config, payloads)
        return manifest

    return run_fallback_tree_sitter_index(repo_root, config, changed_files)


def run_embeddings(repo_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    symbols_path = config["artifacts"]["symbols"]
    if not symbols_path.is_file():
        return run_index(repo_root, config, changed_files=[])

    symbols = json.loads(symbols_path.read_text(encoding="utf-8"))
    chunks = [
        {
            "id": f"chunk:{item['id']}",
            "symbol_id": item["id"],
            "file": item["file"],
            "language": item["language"],
            "start_line": item["start_point"]["row"] + 1,
            "end_line": item["end_point"]["row"] + 1,
            "text": "",
            "embedding": None,
        }
        for item in symbols
        if item["kind"] != "module"
    ]
    chunks.sort(key=lambda item: item["id"])
    config["index_dir"].mkdir(parents=True, exist_ok=True)
    config["artifacts"]["chunks"].write_text(render_json(chunks), encoding="utf-8")
    return {"chunk_count": len(chunks)}


def run_query(config: dict[str, Any], query: str) -> dict[str, Any]:
    symbols_path = config["artifacts"]["symbols"]
    files_path = config["artifacts"]["files"]
    symbols = json.loads(symbols_path.read_text(encoding="utf-8")) if symbols_path.is_file() else []
    files = json.loads(files_path.read_text(encoding="utf-8")) if files_path.is_file() else []
    return build_query_results(query, symbols=symbols, files=files)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and query a repo-local AST-first code intelligence index.")
    parser.add_argument("action", choices=["index", "graph", "embeddings", "query", "config"])
    parser.add_argument("--config", dest="config_path", default=str(DEFAULT_CONFIG_PATH), help="Path to index.yaml")
    parser.add_argument("--index-dir", default="", help="Override index artifact directory.")
    parser.add_argument("--engine", default=DEFAULT_ENGINE, help="Parsing engine name.")
    parser.add_argument("--changed-file", dest="changed_files", action="append", default=[], help="Changed file for incremental reindex.")
    parser.add_argument("--query", default="", help="Query string for the query action.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path.cwd().resolve()
    config_path = repo_root / Path(args.config_path)
    config = load_index_config(repo_root=repo_root, config_path=config_path)
    if args.index_dir:
        config["index_dir"] = repo_root / Path(args.index_dir)
        config["artifacts"] = build_artifact_paths(config["index_dir"])
    config["engine"] = args.engine or config["engine"]

    if args.action == "config":
        print(
            render_json(
                {
                    "engine": config["engine"],
                    "languages": config["languages"],
                    "include": config["include"],
                    "exclude": config["exclude"],
                    "incremental": config["incremental"],
                    "index_dir": str(config["index_dir"].relative_to(repo_root)).replace("\\", "/"),
                }
            ),
            end="",
        )
        return 0

    if args.action in {"index", "graph"}:
        manifest = run_index(repo_root, config, [item.replace("\\", "/") for item in args.changed_files])
        print(render_json(manifest), end="")
        return 0

    if args.action == "embeddings":
        result = run_embeddings(repo_root, config)
        print(render_json(result), end="")
        return 0

    if not args.query:
        raise SystemExit("Missing query string. Use --query <symbol-or-pattern>.")
    result = run_query(config, args.query)
    print(render_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
