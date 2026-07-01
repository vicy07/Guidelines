from __future__ import annotations

import os
import sys
from pathlib import Path


def _resolve_guidelines_root(repo_root: Path) -> Path:
    explicit = os.getenv("GUIDELINES_REPO")
    candidates = [Path(explicit)] if explicit else []
    candidates.append(repo_root.parent / "Guidelines")

    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "shared-code-intel" / "code_intel_runner.py").exists():
            return resolved

    raise SystemExit(
        "Cannot resolve Guidelines repository. Set GUIDELINES_REPO or place Guidelines next to the product repository."
    )


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parent
    guidelines_root = _resolve_guidelines_root(repo_root)
    sys.path.insert(0, str(guidelines_root / "shared-code-intel"))

    from code_intel_runner import main as run_code_intel

    return run_code_intel(argv, repo_root=repo_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
