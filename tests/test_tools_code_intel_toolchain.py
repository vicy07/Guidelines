from pathlib import Path
import importlib.util
import sys


def _load_module(path_str: str, module_name: str):
    module_path = Path(path_str)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_load_toolchain_settings_reads_scip_ast_grep_and_fallback_modes(tmp_path):
    module = _load_module("Tools/code-intel/runtime/toolchain.py", "shared_code_intel_toolchain")
    repo_root = tmp_path
    config_path = repo_root / "code-intel" / "config" / "index.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "\n".join(
            [
                "engine: scip",
                "languages:",
                "  - python",
                "include:",
                "  - src",
                "tools:",
                "  scip:",
                "    enabled: true",
                "    indexers:",
                "      python: scip-python index",
                "  ast_grep:",
                "    enabled: true",
                "  ripgrep:",
                "    enabled: true",
                "  fallback_tree_sitter:",
                "    enabled: true",
            ]
        ),
        encoding="utf-8",
    )

    settings = module.load_toolchain_settings(repo_root=repo_root, config_path=config_path)

    assert settings.primary_engine == "scip"
    assert settings.languages == ["python"]
    assert settings.tools["scip"]["enabled"] is True
    assert settings.tools["scip"]["indexers"]["python"] == "scip-python index"
    assert settings.raw_artifacts["scip"] == repo_root / "code-intel" / "index" / "scip"
    assert settings.raw_artifacts["ast_grep"] == repo_root / "code-intel" / "index" / "ast-grep"
