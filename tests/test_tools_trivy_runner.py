from pathlib import Path
import importlib.util
import sys


def _load_shared_runner():
    module_path = Path("Tools/trivy/trivy_runner.py")
    spec = importlib.util.spec_from_file_location("shared_trivy_runner", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_split_csv_trims_and_drops_empty_values():
    module = _load_shared_runner()

    values = module.split_csv("HIGH, CRITICAL, , secret ")

    assert values == ["HIGH", "CRITICAL", "secret"]


def test_build_trivy_command_for_filesystem_scan_includes_expected_flags(tmp_path):
    module = _load_shared_runner()

    config_path = tmp_path / "trivy.yaml"
    ignorefile_path = tmp_path / ".trivyignore"

    command = module.build_trivy_command(
        trivy_path="trivy",
        mode="fs",
        target=".",
        config_path=config_path,
        ignorefile_path=ignorefile_path,
        severity=["HIGH", "CRITICAL"],
        scanners=["vuln", "misconfig", "secret"],
        exit_code="1",
        timeout="10m",
        output_format="table",
        output_path="",
        cache_dir=".trivy-cache",
        skip_dirs=[".git", "node_modules"],
        skip_files=["coverage.xml"],
        extra_args=["--ignore-unfixed"],
    )

    assert command == [
        "trivy",
        "fs",
        "--config",
        str(config_path),
        "--ignorefile",
        str(ignorefile_path),
        "--exit-code",
        "1",
        "--severity",
        "HIGH,CRITICAL",
        "--scanners",
        "vuln,misconfig,secret",
        "--timeout",
        "10m",
        "--format",
        "table",
        "--cache-dir",
        ".trivy-cache",
        "--no-progress",
        "--skip-dirs",
        ".git",
        "--skip-dirs",
        "node_modules",
        "--skip-files",
        "coverage.xml",
        "--ignore-unfixed",
        ".",
    ]


def test_build_trivy_command_for_image_scan_keeps_target_last():
    module = _load_shared_runner()

    command = module.build_trivy_command(
        trivy_path="trivy",
        mode="image",
        target="ghcr.io/acme/service:123",
        config_path=None,
        ignorefile_path=None,
        severity=["HIGH", "CRITICAL"],
        scanners=["vuln", "secret"],
        exit_code="1",
        timeout="15m",
        output_format="sarif",
        output_path="reports/trivy.sarif",
        cache_dir=".trivy-cache",
        skip_dirs=[],
        skip_files=[],
        extra_args=["--ignore-unfixed"],
    )

    assert command[-1] == "ghcr.io/acme/service:123"
    assert "--output" in command
    assert "reports/trivy.sarif" in command
    assert command[:2] == ["trivy", "image"]
