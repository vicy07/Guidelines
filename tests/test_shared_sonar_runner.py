from pathlib import Path
import importlib.util
import sys


def _load_shared_runner():
    module_path = Path("shared-sonar/sonar_runner.py")
    spec = importlib.util.spec_from_file_location("shared_sonar_runner", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_validate_required_reports_accepts_existing_files(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    python_report = repo_root / "coverage.xml"
    js_report = repo_root / "coverage" / "js" / "lcov.info"
    js_report.parent.mkdir(parents=True)
    python_report.write_text("<coverage />", encoding="utf-8")
    js_report.write_text("TN:\n", encoding="utf-8")

    missing = module.find_missing_reports(
        repo_root=repo_root,
        report_paths=["coverage.xml", "coverage/js/lcov.info"],
    )

    assert missing == []


def test_build_scanner_command_includes_repo_specific_defines():
    module = _load_shared_runner()

    command = module.build_scanner_command(
        npx_path="npx",
        scanner_package="@sonar/scan",
        project_key="demo_project",
        socket_timeout="600",
        response_timeout="600",
        plugins_download_timeout="1800",
        extra_defines=["sonar.branch.name=main"],
    )

    assert command == [
        "npx",
        "@sonar/scan",
        "--define",
        "sonar.projectKey=demo_project",
        "--define",
        "sonar.scanner.socketTimeout=600",
        "--define",
        "sonar.scanner.responseTimeout=600",
        "--define",
        "sonar.plugins.download.timeout=1800",
        "--define",
        "sonar.branch.name=main",
    ]
