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


def test_build_project_status_url_includes_branch_query():
    module = _load_shared_runner()

    url = module.build_project_status_url(
        host_url="https://sonarqube.example.com",
        project_key="demo_project",
        branch="main",
    )

    assert url == (
        "https://sonarqube.example.com/api/qualitygates/project_status"
        "?projectKey=demo_project&branch=main"
    )


def test_load_report_task_reads_scanner_metadata(tmp_path):
    module = _load_shared_runner()

    scannerwork = tmp_path / ".scannerwork"
    scannerwork.mkdir()
    (scannerwork / "report-task.txt").write_text(
        "projectKey=demo_project\nceTaskId=task-123\nserverUrl=https://sonarqube.example.com\n",
        encoding="utf-8",
    )

    data = module.load_report_task(tmp_path)

    assert data == {
        "projectKey": "demo_project",
        "ceTaskId": "task-123",
        "serverUrl": "https://sonarqube.example.com",
    }


def test_summarize_quality_gate_conditions_formats_actionable_lines():
    module = _load_shared_runner()

    lines = module.summarize_quality_gate_conditions(
        [
            {
                "metricKey": "new_coverage",
                "status": "ERROR",
                "actualValue": "76.1",
                "comparator": "LT",
                "errorThreshold": "80",
            }
        ]
    )

    assert lines == ["new_coverage: ERROR (actual=76.1, gate=LT 80)"]
