from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class DockerUnavailableError(RuntimeError):
    pass


def resolve_docker_path() -> str:
    docker_path = shutil.which("docker") or shutil.which("docker.exe")
    if docker_path:
        return docker_path
    raise DockerUnavailableError("Missing 'docker' in PATH. Install Docker before running audit scanners.")


def ensure_docker_ready(docker_path: str) -> None:
    result = subprocess.run(
        [docker_path, "info", "--format", "{{.ServerVersion}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return
    message = result.stderr.strip() or result.stdout.strip() or "unknown Docker daemon error"
    raise DockerUnavailableError(f"Docker daemon is unavailable. Start Docker and retry. Details: {message}")


def run_docker(
    *,
    docker_path: str,
    repo_root: Path,
    image: str,
    container_args: list[str],
    extra_run_args: list[str] | None = None,
) -> int:
    cmd = [
        docker_path,
        "run",
        "--rm",
        "-v",
        f"{repo_root.resolve()}:/workspace",
        "-w",
        "/workspace",
        *(extra_run_args or []),
        image,
        *container_args,
    ]
    print(f"Running: {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=repo_root, check=False).returncode
