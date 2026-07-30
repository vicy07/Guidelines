from pathlib import Path
import importlib.util
import sys


def _load_sonar_adapter():
    module_path = Path("Tools/audits/audits_runtime/scanners/sonar.py")
    spec = importlib.util.spec_from_file_location("shared_audits_sonar_adapter", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_guidelines_root_contains_shared_sonar_runner():
    module = _load_sonar_adapter()

    runner_path = module._guidelines_root() / "Tools" / "sonar" / "sonar_runner.py"

    assert runner_path.is_file()


def test_load_runner_resolves_shared_sonar_contract():
    module = _load_sonar_adapter()

    namespace = module._load_runner()

    assert callable(namespace["run_shared_sonar"])
    assert namespace["SharedSonarConfig"].__name__ == "SharedSonarConfig"
