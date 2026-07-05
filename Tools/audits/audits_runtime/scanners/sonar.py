from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


CoverageCommandBuilder = Callable[[list[str], str], list[list[str]]]


@dataclass(frozen=True)
class SonarScannerConfig:
    repo_root: Path
    default_host_url: str
    default_project_key: str
    coverage_report_paths: tuple[str, ...] = ()
    coverage_command_builder: CoverageCommandBuilder | None = None
    scanner_package: str = "@sonar/scan"
    default_socket_timeout: str = "600"
    default_response_timeout: str = "600"
    default_plugins_download_timeout: str = "1800"
    default_quality_gate_timeout: str = "180"
    default_quality_gate_poll_interval: str = "5"
    global_env_path: Path = field(default_factory=lambda: Path.home() / ".sonar.env")
    local_env_filename: str = ".sonar.env"


def _guidelines_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_runner():
    runner_path = _guidelines_root() / "Tools" / "sonar" / "sonar_runner.py"
    namespace: dict[str, object] = {}
    exec(runner_path.read_text(encoding="utf-8"), namespace)
    return namespace


def run_sonar(action: str, args: list[str], config: SonarScannerConfig) -> dict:
    namespace = _load_runner()
    shared_config = namespace["SharedSonarConfig"](
        repo_root=config.repo_root,
        default_host_url=config.default_host_url,
        default_project_key=config.default_project_key,
        coverage_report_paths=config.coverage_report_paths,
        coverage_command_builder=config.coverage_command_builder,
        scanner_package=config.scanner_package,
        default_socket_timeout=config.default_socket_timeout,
        default_response_timeout=config.default_response_timeout,
        default_plugins_download_timeout=config.default_plugins_download_timeout,
        default_quality_gate_timeout=config.default_quality_gate_timeout,
        default_quality_gate_poll_interval=config.default_quality_gate_poll_interval,
        global_env_path=config.global_env_path,
        local_env_filename=config.local_env_filename,
    )

    if action == "config":
        run_args = [*args, "--show-config"]
    elif action == "scan":
        run_args = args
    else:
        raise SystemExit(f"Unsupported Sonar action: {action}")

    if action == "config" and not any(flag.startswith("--token") for flag in run_args):
        run_args = ["--token", "show-config-placeholder", *run_args]

    exit_code = namespace["run_shared_sonar"](shared_config, run_args)
    return {"status": exit_code, "report": None}


def build_npm_coverage_command(_python_launcher: list[str], _npx_path: str) -> list[list[str]]:
    npm_path = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm_path:
        raise FileNotFoundError("Missing npm on PATH. Install Node.js before running SonarQube scans.")
    return [[npm_path, "run", "test:coverage"]]
