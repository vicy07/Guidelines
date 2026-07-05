from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROLE_DEFINITION = 1
ROLE_IMPORT = 2
SCIP_KIND_MAP = {
    "module": "module",
    "namespace": "module",
    "package": "module",
    "file": "module",
    "function": "function",
    "method": "method",
    "staticmethod": "method",
    "classmethod": "method",
    "class": "class",
    "interface": "interface",
    "protocol": "interface",
    "trait": "interface",
}


def run_scip_index(command: str, repo_root: Path, output_path: Path) -> int:
    cmd = command.split() + ["--output", str(output_path)]
    return subprocess.run(cmd, cwd=repo_root, check=False).returncode


def load_scip_json(output_path: Path, repo_root: Path) -> dict[str, Any]:
    sidecar_path = output_path.with_suffix(f"{output_path.suffix}.json")
    if sidecar_path.is_file():
        return json.loads(sidecar_path.read_text(encoding="utf-8"))

    if output_path.is_file():
        raw_text = output_path.read_text(encoding="utf-8", errors="ignore").strip()
        if raw_text.startswith("{"):
            return json.loads(raw_text)

    result = subprocess.run(
        ["scip", "print", "--json", str(output_path)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "scip print failed")
    payload = json.loads(result.stdout or "{}")
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def _normalize_range(raw_range: Any) -> dict[str, dict[str, int]]:
    if isinstance(raw_range, list):
        if len(raw_range) == 3:
            row, start_column, end_column = raw_range
            return {
                "start": {"row": int(row), "column": int(start_column)},
                "end": {"row": int(row), "column": int(end_column)},
            }
        if len(raw_range) == 4:
            start_row, start_column, end_row, end_column = raw_range
            return {
                "start": {"row": int(start_row), "column": int(start_column)},
                "end": {"row": int(end_row), "column": int(end_column)},
            }
    if isinstance(raw_range, dict):
        start = raw_range.get("start") or {}
        end = raw_range.get("end") or {}
        return {
            "start": {
                "row": int(start.get("line", start.get("row", 0))),
                "column": int(start.get("column", start.get("character", 0))),
            },
            "end": {
                "row": int(end.get("line", end.get("row", 0))),
                "column": int(end.get("column", end.get("character", 0))),
            },
        }
    return {
        "start": {"row": 0, "column": 0},
        "end": {"row": 0, "column": 0},
    }


def _build_symbol_id(language: str, relative_path: str, name: str, start_row: int) -> str:
    return f"{language}:{relative_path}:{name}:{start_row + 1}"


def _occurrence_roles(occurrence: dict[str, Any]) -> int:
    return int(occurrence.get("symbolRoles", occurrence.get("symbol_roles", 0)) or 0)


def _normalize_kind(raw_kind: Any, symbol: str, enclosing_symbol: str) -> str:
    if isinstance(raw_kind, str):
        normalized = SCIP_KIND_MAP.get(raw_kind.strip().lower(), "")
        if normalized:
            return normalized
    if "#" in symbol:
        return "class"
    if "()" in symbol:
        return "method" if enclosing_symbol else "function"
    return "function"


def _symbol_name(symbol: str) -> str:
    matches = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", symbol.replace("`", ""))
    if not matches:
        return "<symbol>"
    return matches[-1]


def _definition_occurrences(document: dict[str, Any]) -> dict[str, dict[str, dict[str, int]]]:
    definitions: dict[str, dict[str, dict[str, int]]] = {}
    for occurrence in document.get("occurrences") or []:
        symbol = str(occurrence.get("symbol") or "")
        roles = _occurrence_roles(occurrence)
        if not symbol or not (roles & ROLE_DEFINITION):
            continue
        definitions.setdefault(symbol, _normalize_range(occurrence.get("range")))
    return definitions


def _resolve_owner_symbol(
    *,
    occurrence_range: dict[str, dict[str, int]],
    symbol_rows_by_id: dict[str, tuple[int, int]],
    module_id: str,
) -> str:
    start_row = occurrence_range["start"]["row"]
    end_row = occurrence_range["end"]["row"]
    candidates: list[tuple[int, str]] = []
    for symbol_id, bounds in symbol_rows_by_id.items():
        symbol_start, symbol_end = bounds
        if symbol_start <= start_row and symbol_end >= end_row:
            candidates.append((symbol_end - symbol_start, symbol_id))
    if not candidates:
        return module_id
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][1]


def normalize_scip_output(payload: dict[str, Any], repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    files: list[dict[str, Any]] = []
    symbols: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str, str]] = set()

    def add_edge(source_id: str, target_id: str, kind: str, file_path: str) -> None:
        key = (source_id, target_id, kind, file_path)
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append(
            {
                "source_id": source_id,
                "target_id": target_id,
                "kind": kind,
                "file": file_path,
            }
        )

    for document in payload.get("documents") or []:
        relative_path = str(document.get("relativePath") or document.get("relative_path") or "").replace("\\", "/")
        if not relative_path:
            continue
        language = str(document.get("language") or "").lower()
        absolute_path = repo_root / Path(relative_path)
        source_bytes = absolute_path.read_bytes() if absolute_path.is_file() else b""
        line_count = source_bytes.decode("utf-8", errors="ignore").count("\n")

        module_id = _build_symbol_id(language, relative_path, "<module>", 0)
        document_symbols = [
            {
                "id": module_id,
                "name": "<module>",
                "kind": "module",
                "language": language,
                "file": relative_path,
                "parent_id": "",
                "start_point": {"row": 0, "column": 0},
                "end_point": {"row": line_count, "column": 0},
            }
        ]
        definitions = _definition_occurrences(document)
        symbol_ids_by_scip: dict[str, str] = {}
        pending_parents: list[tuple[str, str]] = []

        for symbol_info in document.get("symbols") or []:
            scip_symbol = str(symbol_info.get("symbol") or "")
            if not scip_symbol or scip_symbol not in definitions:
                continue
            definition_range = definitions[scip_symbol]
            enclosing_symbol = str(symbol_info.get("enclosingSymbol") or symbol_info.get("enclosing_symbol") or "")
            kind = _normalize_kind(symbol_info.get("kind"), scip_symbol, enclosing_symbol)
            if kind == "module":
                continue
            name = _symbol_name(scip_symbol)
            symbol_id = _build_symbol_id(language, relative_path, name, definition_range["start"]["row"])
            symbol_ids_by_scip[scip_symbol] = symbol_id
            document_symbols.append(
                {
                    "id": symbol_id,
                    "name": name,
                    "kind": kind,
                    "language": language,
                    "file": relative_path,
                    "parent_id": "",
                    "start_point": definition_range["start"],
                    "end_point": definition_range["end"],
                }
            )
            pending_parents.append((symbol_id, enclosing_symbol))

        for symbol in document_symbols:
            if symbol["kind"] == "module":
                continue
            enclosing_symbol = next((parent for current_id, parent in pending_parents if current_id == symbol["id"]), "")
            parent_id = symbol_ids_by_scip.get(enclosing_symbol, module_id)
            symbol["parent_id"] = parent_id
            add_edge(parent_id, str(symbol["id"]), "contain", relative_path)

        owner_rows_by_id: dict[str, tuple[int, int]] = {}
        ordered_symbols = sorted(
            [item for item in document_symbols if item["kind"] != "module"],
            key=lambda item: (item["start_point"]["row"], item["id"]),
        )
        for index, symbol in enumerate(ordered_symbols):
            start_row = int(symbol["start_point"]["row"])
            end_row = int(symbol["end_point"]["row"])
            next_start_row = line_count + 1
            for later in ordered_symbols[index + 1 :]:
                if later["parent_id"] == symbol["parent_id"]:
                    next_start_row = int(later["start_point"]["row"])
                    break
            owner_rows_by_id[str(symbol["id"])] = (
                start_row,
                max(end_row, next_start_row - 1),
            )

        files.append(
            {
                "path": relative_path,
                "language": language,
                "sha256": hashlib.sha256(source_bytes).hexdigest(),
                "bytes": len(source_bytes),
                "symbol_count": len(document_symbols),
                "status": "indexed",
            }
        )
        symbols.extend(document_symbols)

        for occurrence in document.get("occurrences") or []:
            scip_symbol = str(occurrence.get("symbol") or "")
            roles = _occurrence_roles(occurrence)
            if not scip_symbol or (roles & ROLE_DEFINITION):
                continue
            occurrence_range = _normalize_range(occurrence.get("range"))
            owner_symbol_id = _resolve_owner_symbol(
                occurrence_range=occurrence_range,
                symbol_rows_by_id=owner_rows_by_id,
                module_id=module_id,
            )
            target_id = symbol_ids_by_scip.get(scip_symbol, f"external:{scip_symbol}")
            edge_kind = "import" if (roles & ROLE_IMPORT) else "reference"
            add_edge(owner_symbol_id, target_id, edge_kind, relative_path)

    files.sort(key=lambda item: item["path"])
    symbols.sort(key=lambda item: item["id"])
    edges.sort(key=lambda item: (item["file"], item["source_id"], item["target_id"], item["kind"]))
    return files, symbols, edges
