from __future__ import annotations

from collections.abc import Mapping
from typing import Callable

from .types import AllPlanStep, Scanner


def _print_lines(result: dict) -> None:
    for line in result.get("printed", []):
        print(line)


def _normalize_args(argv: list[str]) -> tuple[str, str, list[str]]:
    if not argv:
        raise SystemExit(
            "Usage: python audits.py <scanner|all> <action> [args...]\n"
            "Examples:\n"
            "  python audits.py trivy scan --format json\n"
            "  python audits.py sonar scan\n"
            "  python audits.py eol check\n"
            "  python audits.py all"
        )

    scanner = argv[0]
    if scanner == "all":
        return scanner, "run", argv[1:]

    if len(argv) < 2:
        raise SystemExit(f"Missing action for scanner '{scanner}'.")
    return scanner, argv[1], argv[2:]


def run_cli(
    argv: list[str],
    *,
    scanners: Mapping[str, Scanner],
    all_plan: list[AllPlanStep],
    write_index: Callable[[list[dict]], object],
) -> int:
    scanner, action, remainder = _normalize_args(list(argv or []))

    if scanner == "all":
        results: list[dict] = []
        for scanner_name, scanner_action, resolver in all_plan:
            scanner_module = scanners.get(scanner_name)
            if scanner_module is None:
                raise SystemExit(f"Unsupported scanner in all-plan: {scanner_name}")
            scanner_args = resolver(remainder)
            result = scanner_module.run(scanner_action, scanner_args)
            _print_lines(result)
            results.append({"scanner": scanner_name, "action": scanner_action, **result})
        write_index(results)
        return 0 if all(item["status"] == 0 for item in results) else 1

    scanner_module = scanners.get(scanner)
    if scanner_module is None:
        raise SystemExit(f"Unsupported scanner: {scanner}")

    result = scanner_module.run(action, remainder)
    _print_lines(result)
    write_index([{"scanner": scanner, "action": action, **result}])
    return int(result["status"])
