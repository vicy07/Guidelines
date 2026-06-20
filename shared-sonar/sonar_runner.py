from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence


CoverageCommandBuilder = Callable[[list[str], str], list[list[str]]]


@dataclass(frozen=True)
class SharedSonarConfig:
    repo_root: Path
    default_host_url: str
    default_project_key: str
    coverage_report_paths: tuple[str, ...] = ()
    coverage_command_builder: CoverageCommandBuilder | None = None
    scanner_package: str = "@sonar/scan"
    default_socket_timeout: str = "600"
    default_response_timeout: str = "600"
    default_plugins_download_timeout: str = "1800"
    global_env_path: Path = field(default_factory=lambda: Path.home() / ".sonar.env")
    local_env_filename: str = ".sonar.env"


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            values[key] = value
    return values


def resolve_setting(*sources: str | None) -> str:
    for value in sources:
        if value is None:
            continue
        value = value.strip()
        if value:
            return value
    return ""


def ensure_removed(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def find_missing_reports(*, repo_root: Path, report_paths: Sequence[str]) -> list[str]:
    missing: list[str] = []
    for report_path in report_paths:
        report = repo_root / report_path
        if not report.is_file():
            missing.append(report_path.replace("\\", "/"))
    return missing


def build_scanner_command(
    *,
    npx_path: str,
    scanner_package: str,
    project_key: str,
    socket_timeout: str,
    response_timeout: str,
    plugins_download_timeout: str,
    extra_defines: Sequence[str],
) -> list[str]:
    cmd = [
        npx_path,
        scanner_package,
        "--define",
        f"sonar.projectKey={project_key}",
        "--define",
        f"sonar.scanner.socketTimeout={socket_timeout}",
        "--define",
        f"sonar.scanner.responseTimeout={response_timeout}",
        "--define",
        f"sonar.plugins.download.timeout={plugins_download_timeout}",
    ]
    for define in extra_defines:
        define = define.strip()
        if define:
            cmd.extend(["--define", define])
    return cmd


def run_command(cmd: list[str], *, repo_root: Path, env: dict[str, str], description: str) -> int:
    print(description, flush=True)
    return subprocess.run(cmd, cwd=repo_root, env=env, check=False).returncode


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local SonarQube scan for this repository.")
    parser.add_argument("--host-url", help="SonarQube server URL.")
    parser.add_argument("--token", help="SonarQube user token.")
    parser.add_argument("--project-key", default="", help="SonarQube project key.")
    parser.add_argument("--socket-timeout", default="", help="Scanner socket timeout in seconds.")
    parser.add_argument("--response-timeout", default="", help="Scanner response timeout in seconds.")
    parser.add_argument(
        "--plugins-download-timeout",
        default="",
        help="Plugin download timeout in seconds.",
    )
    parser.add_argument(
        "--define",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Additional sonar analysis property. Repeat as needed.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print resolved non-secret config before running the scan.",
    )
    parser.add_argument(
        "--skip-coverage",
        action="store_true",
        help="Skip Python and JavaScript coverage generation before the SonarQube scan.",
    )
    return parser.parse_args(argv)


def run_shared_sonar(config: SharedSonarConfig, argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    repo_root = config.repo_root.resolve()
    local_env_path = repo_root / config.local_env_filename

    global_env = parse_env_file(config.global_env_path)
    local_env = parse_env_file(local_env_path)

    host_url = resolve_setting(
        args.host_url,
        os.getenv("SONAR_HOST_URL"),
        local_env.get("SONAR_HOST_URL"),
        global_env.get("SONAR_HOST_URL"),
        config.default_host_url,
    )
    token = resolve_setting(
        args.token,
        os.getenv("SONAR_TOKEN"),
        local_env.get("SONAR_TOKEN"),
        global_env.get("SONAR_TOKEN"),
    )
    project_key = resolve_setting(
        args.project_key,
        os.getenv("SONAR_PROJECT_KEY"),
        local_env.get("SONAR_PROJECT_KEY"),
        global_env.get("SONAR_PROJECT_KEY"),
        config.default_project_key,
    )
    socket_timeout = resolve_setting(
        args.socket_timeout,
        os.getenv("SONAR_SCANNER_SOCKET_TIMEOUT"),
        local_env.get("SONAR_SCANNER_SOCKET_TIMEOUT"),
        global_env.get("SONAR_SCANNER_SOCKET_TIMEOUT"),
        config.default_socket_timeout,
    )
    response_timeout = resolve_setting(
        args.response_timeout,
        os.getenv("SONAR_SCANNER_RESPONSE_TIMEOUT"),
        local_env.get("SONAR_SCANNER_RESPONSE_TIMEOUT"),
        global_env.get("SONAR_SCANNER_RESPONSE_TIMEOUT"),
        config.default_response_timeout,
    )
    plugins_download_timeout = resolve_setting(
        args.plugins_download_timeout,
        os.getenv("SONAR_PLUGINS_DOWNLOAD_TIMEOUT"),
        local_env.get("SONAR_PLUGINS_DOWNLOAD_TIMEOUT"),
        global_env.get("SONAR_PLUGINS_DOWNLOAD_TIMEOUT"),
        config.default_plugins_download_timeout,
    )

    if not token:
        print(
            "Missing SONAR_TOKEN. Set it in ~/.sonar.env, ./.sonar.env, SONAR_TOKEN, or pass --token.",
            file=sys.stderr,
        )
        return 1

    npx_path = shutil.which("npx")
    if not npx_path:
        print("Missing 'npx' in PATH. Install Node.js and npm before running the scan.", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["SONAR_HOST_URL"] = host_url
    env["SONAR_TOKEN"] = token

    python_launcher = [sys.executable]

    if args.show_config:
        print(f"Repo root: {repo_root}")
        print(f"Sonar host URL: {host_url}")
        print(f"Sonar project key: {project_key}")
        print(f"Scanner package: {config.scanner_package}")
        print(f"Python launcher: {' '.join(python_launcher)}")
        print(f"Socket timeout: {socket_timeout}")
        print(f"Response timeout: {response_timeout}")
        print(f"Plugin download timeout: {plugins_download_timeout}")
        print(
            "Coverage reports: "
            + (", ".join(config.coverage_report_paths) if config.coverage_report_paths else "none")
        )
        print(f"Skip coverage: {args.skip_coverage}")
        print(f"Additional defines: {args.define or 'none'}")
        print(f"Global config: {config.global_env_path if config.global_env_path.exists() else 'missing'}")
        print(f"Local config: {local_env_path if local_env_path.exists() else 'missing'}")

    if not args.skip_coverage and config.coverage_command_builder is not None:
        for report_path in config.coverage_report_paths:
            ensure_removed(repo_root / report_path)
        for cmd in config.coverage_command_builder(python_launcher, npx_path):
            exit_code = run_command(cmd, repo_root=repo_root, env=env, description=f"Running: {' '.join(cmd)}")
            if exit_code != 0:
                return exit_code
        missing = find_missing_reports(repo_root=repo_root, report_paths=config.coverage_report_paths)
        if missing:
            print(
                f"Coverage reports were not generated: {', '.join(missing)}",
                file=sys.stderr,
            )
            return 1

    cmd = build_scanner_command(
        npx_path=npx_path,
        scanner_package=config.scanner_package,
        project_key=project_key,
        socket_timeout=socket_timeout,
        response_timeout=response_timeout,
        plugins_download_timeout=plugins_download_timeout,
        extra_defines=args.define,
    )
    print(f"Running SonarScanner for '{project_key}' against {host_url}", flush=True)
    return subprocess.run(cmd, cwd=repo_root, env=env, check=False).returncode
