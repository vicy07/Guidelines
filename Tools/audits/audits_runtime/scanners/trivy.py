from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..docker_runner import ensure_docker_ready, resolve_docker_path, run_docker
from ..reporting import ensure_reports_root, report_path


@dataclass(frozen=True)
class TrivyScannerConfig:
    repo_root: Path
    reports_dir: tuple[str, ...] = ("reports", "audits")
    docker_image: str = "aquasec/trivy:latest"
    cache_volume: str = "trivy-cache"
    config_filename: str = "trivy.yaml"
    ignore_filename: str = ".trivyignore"
    severity: tuple[str, ...] = ("HIGH", "CRITICAL")
    scanners: tuple[str, ...] = ("vuln", "misconfig", "secret")
    timeout: str = "10m"
    exit_code: str = "1"


def _format_to_trivy(output_format: str) -> str:
    return {"console": "table", "json": "json", "sarif": "sarif"}[output_format]


def _config_path(config: TrivyScannerConfig) -> Path:
    return config.repo_root / config.config_filename


def _ignore_path(config: TrivyScannerConfig) -> Path:
    return config.repo_root / config.ignore_filename


def _build_common_args(
    config: TrivyScannerConfig,
    output_format: str,
    output_path: Path | None,
) -> list[str]:
    args = [
        "--cache-dir",
        "/root/.cache/trivy",
        "--config",
        config.config_filename,
        "--severity",
        ",".join(config.severity),
        "--scanners",
        ",".join(config.scanners),
        "--timeout",
        config.timeout,
        "--exit-code",
        config.exit_code,
        "--format",
        _format_to_trivy(output_format),
        "--no-progress",
    ]
    ignore_path = _ignore_path(config)
    if ignore_path.is_file():
        args.extend(["--ignorefile", config.ignore_filename])
    if output_path is not None:
        args.extend(["--output", str(output_path.relative_to(config.repo_root)).replace("\\", "/")])
    return args


def _extra_run_args(config: TrivyScannerConfig) -> list[str]:
    return ["-v", f"{config.cache_volume}:/root/.cache/trivy"]


def _local_image_exists(docker_path: str, image_ref: str) -> bool:
    result = subprocess.run(
        [docker_path, "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _save_image_archive(config: TrivyScannerConfig, docker_path: str, image_ref: str) -> Path:
    temp_dir = ensure_reports_root(config.repo_root, config.reports_dir) / "_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    archive_path = temp_dir / f"{image_ref.replace('/', '_').replace(':', '_')}.tar"
    result = subprocess.run(
        [docker_path, "save", "-o", str(archive_path), image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown docker save error"
        raise RuntimeError(f"Failed to export Docker image '{image_ref}'. Details: {message}")
    return archive_path


def run_trivy(action: str, args: list[str], config: TrivyScannerConfig) -> dict:
    repo_root = config.repo_root.resolve()
    config_path = _config_path(config)
    ignore_path = _ignore_path(config)

    if action == "config":
        docker_path = shutil.which("docker") or shutil.which("docker.exe") or "missing"
        return {
            "status": 0,
            "printed": [
                f"Repo root: {repo_root}",
                "Mode: fs",
                "Target: .",
                f"Docker path: {docker_path}",
                f"Trivy image: {config.docker_image}",
                f"Cache volume: {config.cache_volume}",
                f"Config path: {config_path}",
                f"Ignore file: {ignore_path if ignore_path.is_file() else 'none'}",
                f"Reports root: {ensure_reports_root(repo_root, config.reports_dir)}",
                "Supported formats: console,json,sarif",
            ],
        }

    docker_path = resolve_docker_path()
    ensure_docker_ready(docker_path)

    if action == "version":
        exit_code = run_docker(
            docker_path=docker_path,
            repo_root=repo_root,
            image=config.docker_image,
            container_args=["--version"],
            extra_run_args=_extra_run_args(config),
        )
        return {"status": exit_code, "report": None}

    if action == "db" and args[:1] == ["update"]:
        exit_code = run_docker(
            docker_path=docker_path,
            repo_root=repo_root,
            image=config.docker_image,
            container_args=[
                "image",
                "--download-db-only",
                "--cache-dir",
                "/root/.cache/trivy",
                "--no-progress",
            ],
            extra_run_args=_extra_run_args(config),
        )
        return {"status": exit_code, "report": None}

    output_format = "console"
    extra_args = list(args)
    if action in {"scan", "image"} and extra_args[:2] == ["--format", "json"]:
        output_format = "json"
        extra_args = extra_args[2:]
    elif action in {"scan", "image"} and extra_args[:2] == ["--format", "sarif"]:
        output_format = "sarif"
        extra_args = extra_args[2:]
    elif action in {"scan", "image"} and extra_args[:2] == ["--format", "console"]:
        output_format = "console"
        extra_args = extra_args[2:]

    if action == "scan":
        target = extra_args[0] if extra_args else "."
        report = None if output_format == "console" else report_path(repo_root, "trivy", "fs", output_format, config.reports_dir)
        exit_code = run_docker(
            docker_path=docker_path,
            repo_root=repo_root,
            image=config.docker_image,
            container_args=["fs", *_build_common_args(config, output_format, report), target],
            extra_run_args=_extra_run_args(config),
        )
        printed = [] if report is None else [f"Report: {report}"]
        return {"status": exit_code, "report": str(report) if report else None, "printed": printed}

    if action == "image":
        if not extra_args:
            raise SystemExit("Missing image reference. Use: python audits.py trivy image <image-ref>")
        image_ref = extra_args[0]
        report = None if output_format == "console" else report_path(
            repo_root,
            "trivy",
            f"image-{image_ref}",
            output_format,
            config.reports_dir,
        )
        archive_path: Path | None = None
        try:
            if _local_image_exists(docker_path, image_ref):
                archive_path = _save_image_archive(config, docker_path, image_ref)
                container_args = [
                    "image",
                    *_build_common_args(config, output_format, report),
                    "--input",
                    str(archive_path.relative_to(repo_root)).replace("\\", "/"),
                ]
            else:
                container_args = ["image", *_build_common_args(config, output_format, report), image_ref]
            exit_code = run_docker(
                docker_path=docker_path,
                repo_root=repo_root,
                image=config.docker_image,
                container_args=container_args,
                extra_run_args=_extra_run_args(config),
            )
            printed = [] if report is None else [f"Report: {report}"]
            return {"status": exit_code, "report": str(report) if report else None, "printed": printed}
        finally:
            if archive_path and archive_path.exists():
                archive_path.unlink()

    raise SystemExit(f"Unsupported Trivy action: {action}")
