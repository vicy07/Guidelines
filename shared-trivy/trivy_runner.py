from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class SharedTrivyConfig:
    repo_root: Path
    default_mode: str = "fs"
    default_fs_target: str = "."
    default_image_ref: str = ""
    default_severity: str = "HIGH,CRITICAL"
    default_scanners: tuple[str, ...] = ("vuln", "misconfig", "secret")
    default_exit_code: str = "1"
    default_timeout: str = "10m"
    default_format: str = "table"
    default_cache_dir: str = ".trivy-cache"
    default_config_filename: str = "trivy.yaml"
    default_ignore_filename: str = ".trivyignore"
    default_skip_dirs: tuple[str, ...] = (".git", ".venv", "node_modules")
    default_skip_files: tuple[str, ...] = ()
    global_env_path: Path = field(default_factory=lambda: Path.home() / ".trivy.env")
    local_env_filename: str = ".trivy.env"


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


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        item = value.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def resolve_repo_path(repo_root: Path, candidate: str) -> Path:
    path = Path(candidate)
    if not path.is_absolute():
        path = repo_root / path
    return path


def build_trivy_command(
    *,
    trivy_path: str,
    mode: str,
    target: str,
    config_path: Path | None,
    ignorefile_path: Path | None,
    severity: Sequence[str],
    scanners: Sequence[str],
    exit_code: str,
    timeout: str,
    output_format: str,
    output_path: str,
    cache_dir: str,
    skip_dirs: Sequence[str],
    skip_files: Sequence[str],
    extra_args: Sequence[str],
) -> list[str]:
    if mode not in {"fs", "image"}:
        raise ValueError(f"Unsupported Trivy mode: {mode}")

    cmd = [trivy_path, mode]
    if config_path is not None:
        cmd.extend(["--config", str(config_path)])
    if ignorefile_path is not None:
        cmd.extend(["--ignorefile", str(ignorefile_path)])
    cmd.extend(
        [
            "--exit-code",
            exit_code,
            "--severity",
            ",".join(severity),
            "--scanners",
            ",".join(scanners),
            "--timeout",
            timeout,
            "--format",
            output_format,
            "--cache-dir",
            cache_dir,
            "--no-progress",
        ]
    )
    if output_path:
        cmd.extend(["--output", output_path])
    for skip_dir in skip_dirs:
        cmd.extend(["--skip-dirs", skip_dir])
    for skip_file in skip_files:
        cmd.extend(["--skip-files", skip_file])
    cmd.extend(extra_args)
    cmd.append(target)
    return cmd


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local Trivy scan for this repository.")
    parser.add_argument("mode", nargs="?", choices=["fs", "image"], default="", help="Scan mode.")
    parser.add_argument("target", nargs="?", default="", help="Filesystem path or image reference.")
    parser.add_argument("--config", default="", help="Path to trivy.yaml.")
    parser.add_argument("--ignorefile", default="", help="Path to .trivyignore.")
    parser.add_argument("--severity", default="", help="Comma-separated severities.")
    parser.add_argument("--scanners", default="", help="Comma-separated scanners.")
    parser.add_argument("--exit-code", dest="exit_code", default="", help="Exit code when findings exist.")
    parser.add_argument("--timeout", default="", help="Trivy timeout.")
    parser.add_argument("--format", dest="output_format", default="", help="Output format.")
    parser.add_argument("--output", default="", help="Optional output file path.")
    parser.add_argument("--cache-dir", default="", help="Trivy cache directory.")
    parser.add_argument("--skip-dir", dest="skip_dirs", action="append", default=[], help="Directory to skip.")
    parser.add_argument("--skip-file", dest="skip_files", action="append", default=[], help="File to skip.")
    parser.add_argument(
        "--arg",
        dest="extra_args",
        action="append",
        default=[],
        metavar="FLAG",
        help="Additional Trivy argument to append before the target.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print resolved non-secret config and exit without running Trivy.",
    )
    return parser.parse_args(argv)


def run_shared_trivy(config: SharedTrivyConfig, argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    repo_root = config.repo_root.resolve()
    local_env_path = repo_root / config.local_env_filename
    global_env = parse_env_file(config.global_env_path)
    local_env = parse_env_file(local_env_path)

    mode = resolve_setting(
        args.mode,
        os.getenv("TRIVY_SCAN_MODE"),
        local_env.get("TRIVY_SCAN_MODE"),
        global_env.get("TRIVY_SCAN_MODE"),
        config.default_mode,
    ).lower()
    if mode not in {"fs", "image"}:
        print(f"Unsupported Trivy mode: {mode}", file=sys.stderr)
        return 1

    target_key = "TRIVY_FS_TARGET" if mode == "fs" else "TRIVY_IMAGE_REF"
    default_target = config.default_fs_target if mode == "fs" else config.default_image_ref
    target = resolve_setting(
        args.target,
        os.getenv(target_key),
        local_env.get(target_key),
        global_env.get(target_key),
        default_target,
    )
    if not target:
        expected = "filesystem path" if mode == "fs" else "image reference"
        print(f"Missing Trivy {expected}. Pass it on the CLI or set {target_key}.", file=sys.stderr)
        return 1

    severity = split_csv(
        resolve_setting(
            args.severity,
            os.getenv("TRIVY_SEVERITY"),
            local_env.get("TRIVY_SEVERITY"),
            global_env.get("TRIVY_SEVERITY"),
            config.default_severity,
        )
    )
    scanners = split_csv(
        resolve_setting(
            args.scanners,
            os.getenv("TRIVY_SCANNERS"),
            local_env.get("TRIVY_SCANNERS"),
            global_env.get("TRIVY_SCANNERS"),
            ",".join(config.default_scanners),
        )
    )
    exit_code = resolve_setting(
        args.exit_code,
        os.getenv("TRIVY_EXIT_CODE"),
        local_env.get("TRIVY_EXIT_CODE"),
        global_env.get("TRIVY_EXIT_CODE"),
        config.default_exit_code,
    )
    timeout = resolve_setting(
        args.timeout,
        os.getenv("TRIVY_TIMEOUT"),
        local_env.get("TRIVY_TIMEOUT"),
        global_env.get("TRIVY_TIMEOUT"),
        config.default_timeout,
    )
    output_format = resolve_setting(
        args.output_format,
        os.getenv("TRIVY_FORMAT"),
        local_env.get("TRIVY_FORMAT"),
        global_env.get("TRIVY_FORMAT"),
        config.default_format,
    )
    output_path = resolve_setting(
        args.output,
        os.getenv("TRIVY_OUTPUT"),
        local_env.get("TRIVY_OUTPUT"),
        global_env.get("TRIVY_OUTPUT"),
    )

    cache_dir = str(
        resolve_repo_path(
            repo_root,
            resolve_setting(
                args.cache_dir,
                os.getenv("TRIVY_CACHE_DIR"),
                local_env.get("TRIVY_CACHE_DIR"),
                global_env.get("TRIVY_CACHE_DIR"),
                config.default_cache_dir,
            ),
        )
    )

    explicit_config = resolve_setting(
        args.config,
        os.getenv("TRIVY_CONFIG"),
        local_env.get("TRIVY_CONFIG"),
        global_env.get("TRIVY_CONFIG"),
    )
    if explicit_config:
        config_path = resolve_repo_path(repo_root, explicit_config)
        if not config_path.is_file():
            print(f"Missing Trivy config file: {config_path}", file=sys.stderr)
            return 1
    else:
        default_config_path = repo_root / config.default_config_filename
        config_path = default_config_path if default_config_path.is_file() else None

    explicit_ignorefile = resolve_setting(
        args.ignorefile,
        os.getenv("TRIVY_IGNOREFILE"),
        local_env.get("TRIVY_IGNOREFILE"),
        global_env.get("TRIVY_IGNOREFILE"),
    )
    if explicit_ignorefile:
        ignorefile_path = resolve_repo_path(repo_root, explicit_ignorefile)
        if not ignorefile_path.is_file():
            print(f"Missing Trivy ignore file: {ignorefile_path}", file=sys.stderr)
            return 1
    else:
        default_ignorefile_path = repo_root / config.default_ignore_filename
        ignorefile_path = default_ignorefile_path if default_ignorefile_path.is_file() else None

    skip_dirs = unique(
        [
            *config.default_skip_dirs,
            *split_csv(
                resolve_setting(
                    os.getenv("TRIVY_SKIP_DIRS"),
                    local_env.get("TRIVY_SKIP_DIRS"),
                    global_env.get("TRIVY_SKIP_DIRS"),
                )
            ),
            *args.skip_dirs,
        ]
    )
    skip_files = unique(
        [
            *config.default_skip_files,
            *split_csv(
                resolve_setting(
                    os.getenv("TRIVY_SKIP_FILES"),
                    local_env.get("TRIVY_SKIP_FILES"),
                    global_env.get("TRIVY_SKIP_FILES"),
                )
            ),
            *args.skip_files,
        ]
    )

    trivy_path = shutil.which("trivy") or shutil.which("trivy.exe") or ""
    if args.show_config:
        print(f"Repo root: {repo_root}")
        print(f"Mode: {mode}")
        print(f"Target: {target}")
        print(f"Trivy path: {trivy_path or 'missing'}")
        print(f"Config path: {config_path or 'none'}")
        print(f"Ignore file: {ignorefile_path or 'none'}")
        print(f"Severity: {','.join(severity)}")
        print(f"Scanners: {','.join(scanners)}")
        print(f"Exit code: {exit_code}")
        print(f"Timeout: {timeout}")
        print(f"Format: {output_format}")
        print(f"Output: {output_path or 'stdout'}")
        print(f"Cache dir: {cache_dir}")
        print(f"Skip dirs: {', '.join(skip_dirs) if skip_dirs else 'none'}")
        print(f"Skip files: {', '.join(skip_files) if skip_files else 'none'}")
        print(f"Additional args: {args.extra_args or 'none'}")
        print(f"Global config: {config.global_env_path if config.global_env_path.exists() else 'missing'}")
        print(f"Local config: {local_env_path if local_env_path.exists() else 'missing'}")
        return 0

    if not trivy_path:
        print("Missing 'trivy' in PATH. Install Trivy before running the scan.", file=sys.stderr)
        return 1

    cmd = build_trivy_command(
        trivy_path=trivy_path,
        mode=mode,
        target=target,
        config_path=config_path,
        ignorefile_path=ignorefile_path,
        severity=severity,
        scanners=scanners,
        exit_code=exit_code,
        timeout=timeout,
        output_format=output_format,
        output_path=output_path,
        cache_dir=cache_dir,
        skip_dirs=skip_dirs,
        skip_files=skip_files,
        extra_args=args.extra_args,
    )

    print(f"Running Trivy {mode} scan against {target}", flush=True)
    print(f"Running: {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=repo_root, check=False).returncode
