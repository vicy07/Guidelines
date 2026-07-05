from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run_ast_grep_scan(repo_root: Path, pattern: str, language: str) -> list[dict]:
    cmd = ["ast-grep", "run", "-p", pattern, "--lang", language, "--json=stream"]
    result = subprocess.run(cmd, cwd=repo_root, check=False, capture_output=True, text=True)
    if result.returncode not in {0, 8}:
        raise RuntimeError(result.stderr.strip() or "ast-grep failed")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]
