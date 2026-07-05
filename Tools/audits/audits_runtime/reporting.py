from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


def ensure_reports_root(repo_root: Path, reports_dir: tuple[str, ...] = ("reports", "audits")) -> Path:
    target = repo_root.joinpath(*reports_dir)
    target.mkdir(parents=True, exist_ok=True)
    return target


def slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "").strip())
    return text.strip("-._") or "target"


def report_path(
    repo_root: Path,
    scanner: str,
    subject: str,
    output_format: str,
    reports_dir: tuple[str, ...] = ("reports", "audits"),
) -> Path:
    extension = {"json": "json", "sarif": "sarif"}.get(output_format, "txt")
    return ensure_reports_root(repo_root, reports_dir) / f"{slugify(scanner)}-{slugify(subject)}.{extension}"


def write_index(
    repo_root: Path,
    results: list[dict],
    reports_dir: tuple[str, ...] = ("reports", "audits"),
) -> Path:
    target = ensure_reports_root(repo_root, reports_dir) / "index.json"
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target
