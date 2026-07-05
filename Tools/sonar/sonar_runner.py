from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from base64 import b64encode
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import urlencode
from urllib.request import Request, urlopen


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
    default_quality_gate_timeout: str = "180"
    default_quality_gate_poll_interval: str = "5"
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


def run_scanner_command(
    cmd: list[str],
    *,
    repo_root: Path,
    env: dict[str, str],
    description: str,
) -> int:
    print(description, flush=True)
    process = subprocess.Popen(
        cmd,
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
    return process.wait()


def parse_float_setting(value: str, *, name: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric, got: {value}") from exc


def detect_git_branch(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""

    if result.returncode != 0:
        return ""

    branch = result.stdout.strip()
    if not branch or branch == "HEAD":
        return ""
    return branch


def build_api_headers(token: str) -> dict[str, str]:
    encoded = b64encode(f"{token}:".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}


def api_get_json(*, url: str, token: str) -> dict:
    request = Request(url, headers=build_api_headers(token))
    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)
    except Exception:
        curl_path = shutil.which("curl") or shutil.which("curl.exe")
        if not curl_path:
            raise
        result = subprocess.run(
            [curl_path, "-sS", "-u", f"{token}:", url],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"curl failed for {url}: {result.stderr.strip() or result.stdout.strip()}")
        return json.loads(result.stdout)


def load_report_task(repo_root: Path) -> dict[str, str]:
    report_task_path = repo_root / ".scannerwork" / "report-task.txt"
    if not report_task_path.is_file():
        raise FileNotFoundError(f"Missing SonarScanner report task file: {report_task_path}")
    return parse_env_file(report_task_path)


def build_project_status_url(*, host_url: str, project_key: str, branch: str) -> str:
    query = {"projectKey": project_key}
    if branch:
        query["branch"] = branch
    return f"{host_url.rstrip('/')}/api/qualitygates/project_status?{urlencode(query)}"


def wait_for_ce_task(
    *,
    host_url: str,
    token: str,
    ce_task_id: str,
    timeout_seconds: float,
    poll_interval_seconds: float,
) -> dict:
    task_url = f"{host_url.rstrip('/')}/api/ce/task?{urlencode({'id': ce_task_id})}"
    deadline = time.monotonic() + timeout_seconds
    last_status = ""

    while True:
        response = api_get_json(url=task_url, token=token)
        task = response.get("task") or {}
        status = str(task.get("status") or "").strip().upper()
        if status and status != last_status:
            print(f"Sonar CE task status: {status}", flush=True)
            last_status = status
        if status in {"SUCCESS", "FAILED", "CANCELED"}:
            return task
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for Sonar CE task {ce_task_id} after {timeout_seconds:.0f}s")
        time.sleep(poll_interval_seconds)


def summarize_quality_gate_conditions(conditions: Sequence[dict]) -> list[str]:
    lines: list[str] = []
    for condition in conditions:
        metric_key = str(condition.get("metricKey") or "").strip() or "unknown_metric"
        status = str(condition.get("status") or "").strip() or "UNKNOWN"
        actual_value = str(condition.get("actualValue") or "").strip() or "n/a"
        comparator = str(condition.get("comparator") or "").strip() or "?"
        threshold = str(condition.get("errorThreshold") or "").strip() or "n/a"
        lines.append(f"{metric_key}: {status} (actual={actual_value}, gate={comparator} {threshold})")
    return lines


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local SonarQube scan for this repository.")
    parser.add_argument("--host-url", help="SonarQube server URL.")
    parser.add_argument("--token", help="SonarQube user token.")
    parser.add_argument("--project-key", default="", help="SonarQube project key.")
    parser.add_argument("--branch", default="", help="SonarQube branch name. Defaults to the current git branch.")
    parser.add_argument("--socket-timeout", default="", help="Scanner socket timeout in seconds.")
    parser.add_argument("--response-timeout", default="", help="Scanner response timeout in seconds.")
    parser.add_argument(
        "--plugins-download-timeout",
        default="",
        help="Plugin download timeout in seconds.",
    )
    parser.add_argument(
        "--quality-gate-timeout",
        default="",
        help="How long to wait for SonarQube server-side processing before checking the quality gate.",
    )
    parser.add_argument(
        "--quality-gate-poll-interval",
        default="",
        help="Polling interval in seconds while waiting for the SonarQube background task.",
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
        help="Print resolved non-secret config and exit without running coverage or SonarScanner.",
    )
    parser.add_argument(
        "--skip-coverage",
        action="store_true",
        help="Skip Python and JavaScript coverage generation before the SonarQube scan.",
    )
    parser.add_argument(
        "--skip-quality-gate",
        action="store_true",
        help="Skip waiting for SonarQube server processing and quality gate status.",
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
        os.getenv("SONARQUBE_TOKEN"),
        local_env.get("SONAR_TOKEN"),
        local_env.get("SONARQUBE_TOKEN"),
        global_env.get("SONAR_TOKEN"),
        global_env.get("SONARQUBE_TOKEN"),
    )
    project_key = resolve_setting(
        args.project_key,
        os.getenv("SONAR_PROJECT_KEY"),
        local_env.get("SONAR_PROJECT_KEY"),
        global_env.get("SONAR_PROJECT_KEY"),
        config.default_project_key,
    )
    branch = resolve_setting(
        args.branch,
        os.getenv("SONAR_BRANCH"),
        local_env.get("SONAR_BRANCH"),
        global_env.get("SONAR_BRANCH"),
        detect_git_branch(repo_root),
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
    quality_gate_timeout = resolve_setting(
        args.quality_gate_timeout,
        os.getenv("SONAR_QUALITY_GATE_TIMEOUT"),
        local_env.get("SONAR_QUALITY_GATE_TIMEOUT"),
        global_env.get("SONAR_QUALITY_GATE_TIMEOUT"),
        config.default_quality_gate_timeout,
    )
    quality_gate_poll_interval = resolve_setting(
        args.quality_gate_poll_interval,
        os.getenv("SONAR_QUALITY_GATE_POLL_INTERVAL"),
        local_env.get("SONAR_QUALITY_GATE_POLL_INTERVAL"),
        global_env.get("SONAR_QUALITY_GATE_POLL_INTERVAL"),
        config.default_quality_gate_poll_interval,
    )

    if not token:
        print(
            "Missing Sonar token. Set SONAR_TOKEN/SONARQUBE_TOKEN in ~/.sonar.env, ./.sonar.env, env vars, or pass --token.",
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
        print(f"Sonar branch: {branch or 'default'}")
        print(f"Scanner package: {config.scanner_package}")
        print(f"Python launcher: {' '.join(python_launcher)}")
        print(f"Socket timeout: {socket_timeout}")
        print(f"Response timeout: {response_timeout}")
        print(f"Plugin download timeout: {plugins_download_timeout}")
        print(f"Quality gate wait: {not args.skip_quality_gate}")
        print(f"Quality gate timeout: {quality_gate_timeout}")
        print(f"Quality gate poll interval: {quality_gate_poll_interval}")
        print(
            "Coverage reports: "
            + (", ".join(config.coverage_report_paths) if config.coverage_report_paths else "none")
        )
        print(f"Skip coverage: {args.skip_coverage}")
        print(f"Additional defines: {args.define or 'none'}")
        print(f"Global config: {config.global_env_path if config.global_env_path.exists() else 'missing'}")
        print(f"Local config: {local_env_path if local_env_path.exists() else 'missing'}")
        return 0

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
    scanner_exit_code = run_scanner_command(
        cmd,
        repo_root=repo_root,
        env=env,
        description=f"Running: {' '.join(cmd)}",
    )
    if scanner_exit_code != 0:
        return scanner_exit_code

    if args.skip_quality_gate:
        print("Sonar quality gate check skipped.", flush=True)
        return 0

    try:
        timeout_seconds = parse_float_setting(quality_gate_timeout, name="quality gate timeout")
        poll_interval_seconds = parse_float_setting(
            quality_gate_poll_interval,
            name="quality gate poll interval",
        )
        report_task = load_report_task(repo_root)
        ce_task_id = resolve_setting(report_task.get("ceTaskId"))
        if not ce_task_id:
            print("Missing ceTaskId in .scannerwork/report-task.txt.", file=sys.stderr)
            return 1

        print(f"Waiting for SonarQube server task {ce_task_id}...", flush=True)
        task = wait_for_ce_task(
            host_url=host_url,
            token=token,
            ce_task_id=ce_task_id,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        task_status = str(task.get("status") or "").strip().upper()
        if task_status != "SUCCESS":
            print(f"Sonar CE task finished with status {task_status}.", file=sys.stderr)
            if task.get("errorMessage"):
                print(str(task.get("errorMessage")), file=sys.stderr)
            return 1

        status_url = build_project_status_url(
            host_url=host_url,
            project_key=project_key,
            branch=branch,
        )
        status_payload = api_get_json(url=status_url, token=token)
        project_status = status_payload.get("projectStatus") or {}
        gate_status = str(project_status.get("status") or "").strip().upper() or "UNKNOWN"
        condition_lines = summarize_quality_gate_conditions(project_status.get("conditions") or [])
        scope_suffix = f" (branch={branch})" if branch else ""
        print(f"Sonar quality gate for '{project_key}'{scope_suffix}: {gate_status}", flush=True)
        for line in condition_lines:
            print(f"  - {line}", flush=True)
        return 0 if gate_status == "OK" else 1
    except Exception as exc:
        print(f"Failed to verify Sonar quality gate status: {exc}", file=sys.stderr)
        return 1
