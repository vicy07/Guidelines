from pathlib import Path
import importlib.util
import sys
import json


def _load_shared_runner():
    module_path = Path("Tools/code-intel/code_intel_runner.py")
    spec = importlib.util.spec_from_file_location("shared_code_intel_runner", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_index_paths_uses_expected_artifact_names():
    module = _load_shared_runner()

    paths = module.build_index_paths("code-intel/index")

    assert paths == {
        "manifest": Path("code-intel/index/manifest.json"),
        "files": Path("code-intel/index/files.json"),
        "symbols": Path("code-intel/index/symbols.json"),
        "edges": Path("code-intel/index/edges.json"),
        "chunks": Path("code-intel/index/chunks.json"),
    }


def test_normalize_changed_files_sorts_deduplicates_and_normalizes_separators():
    module = _load_shared_runner()

    changed = module.normalize_changed_files(
        ["src\\main.py", "src/main.py", "", "tests\\test_main.py"]
    )

    assert changed == ["src/main.py", "tests/test_main.py"]


def test_build_manifest_includes_revision_engine_and_artifacts():
    module = _load_shared_runner()

    manifest = module.build_manifest(
        tool_version="0.1.0",
        commit_sha="abc1234",
        generated_at="2026-07-01T10:00:00Z",
        index_root="code-intel/index",
        changed_files=["src\\main.py"],
    )

    assert manifest["engine"] == "tree-sitter"
    assert manifest["commit_sha"] == "abc1234"
    assert manifest["changed_files"] == ["src/main.py"]
    assert manifest["artifacts"]["symbols"] == "code-intel/index/symbols.json"


def test_load_runtime_settings_reads_yaml_and_applies_defaults(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    config_path = repo_root / "code-intel" / "config" / "index.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "\n".join(
            [
                "engine: tree-sitter",
                "image: custom/code-intel:1.2.3",
                "languages:",
                "  - python",
                "include:",
                "  - src",
                "exclude:",
                "  - dist",
                "incremental: true",
                "artifacts:",
                "  index_dir: code-intel/generated",
            ]
        ),
        encoding="utf-8",
    )

    settings = module.load_runtime_settings(repo_root=repo_root)

    assert settings["engine"] == "tree-sitter"
    assert settings["image"] == "custom/code-intel:1.2.3"
    assert settings["config_path"] == repo_root / "code-intel" / "config" / "index.yaml"
    assert settings["index_dir"] == repo_root / "code-intel" / "generated"
    assert settings["cache_dir"] == repo_root / ".code-intel-cache"
    assert settings["languages"] == ["python"]
    assert settings["include"] == ["src"]
    assert settings["exclude"] == ["dist"]
    assert settings["incremental"] is True


def test_build_docker_command_for_index_mounts_repo_cache_and_changed_files(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    settings = {
        "image": "guidelines-code-intel:local",
        "config_path": repo_root / "code-intel" / "config" / "index.yaml",
        "index_dir": repo_root / "code-intel" / "index",
        "cache_dir": repo_root / ".code-intel-cache",
        "engine": "tree-sitter",
    }

    command = module.build_docker_command(
        docker_path="docker",
        repo_root=repo_root,
        action="index",
        settings=settings,
        changed_files=["src\\main.py", "tests/test_main.py"],
        extra_args=["--verbose"],
    )

    assert command[:4] == ["docker", "run", "--rm", "-v"]
    assert f"{repo_root.resolve()}:/workspace" in command
    assert f"{(repo_root / '.code-intel-cache').resolve()}:/cache/code-intel" in command
    assert "--config" in command
    assert "code-intel/config/index.yaml" in command
    assert "--index-dir" in command
    assert "code-intel/index" in command
    assert command[-5:] == [
        "--changed-file",
        "src/main.py",
        "--changed-file",
        "tests/test_main.py",
        "--verbose",
    ]


def test_build_docker_command_for_query_places_query_after_separator(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    settings = {
        "image": "guidelines-code-intel:local",
        "config_path": repo_root / "code-intel" / "config" / "index.yaml",
        "index_dir": repo_root / "code-intel" / "index",
        "cache_dir": repo_root / ".code-intel-cache",
        "engine": "tree-sitter",
    }

    command = module.build_docker_command(
        docker_path="docker",
        repo_root=repo_root,
        action="query",
        settings=settings,
        query="MyClass.my_method",
    )

    assert command[-3:] == ["query", "--query", "MyClass.my_method"]


def test_build_docker_command_does_not_repeat_code_intel_entrypoint(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    settings = {
        "image": "guidelines-code-intel:local",
        "config_path": repo_root / "code-intel" / "config" / "index.yaml",
        "index_dir": repo_root / "code-intel" / "index",
        "cache_dir": repo_root / ".code-intel-cache",
        "engine": "scip",
    }

    command = module.build_docker_command(
        docker_path="docker",
        repo_root=repo_root,
        action="index",
        settings=settings,
    )

    image_index = command.index("guidelines-code-intel:local")

    assert command[image_index + 1 : image_index + 5] == [
        "--config",
        "code-intel/config/index.yaml",
        "--index-dir",
        "code-intel/index",
    ]


def test_render_resolved_config_returns_non_secret_json_ready_payload(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    settings = {
        "engine": "tree-sitter",
        "image": "guidelines-code-intel:local",
        "config_path": repo_root / "code-intel" / "config" / "index.yaml",
        "index_dir": repo_root / "code-intel" / "index",
        "cache_dir": repo_root / ".code-intel-cache",
        "languages": ["python", "typescript"],
        "include": ["src"],
        "exclude": ["dist"],
        "incremental": True,
    }

    rendered = module.render_resolved_config(settings)

    payload = json.loads(rendered)
    assert payload == {
        "engine": "tree-sitter",
        "image": "guidelines-code-intel:local",
        "config_path": "code-intel/config/index.yaml",
        "index_dir": "code-intel/index",
        "cache_dir": ".code-intel-cache",
        "languages": ["python", "typescript"],
        "include": ["src"],
        "exclude": ["dist"],
        "incremental": True,
        "tools": {},
    }


def test_render_resolved_config_includes_toolchain_sections(tmp_path):
    module = _load_shared_runner()

    repo_root = tmp_path
    settings = {
        "engine": "scip",
        "image": "guidelines-code-intel:local",
        "config_path": repo_root / "code-intel" / "config" / "index.yaml",
        "index_dir": repo_root / "code-intel" / "index",
        "cache_dir": repo_root / ".code-intel-cache",
        "languages": ["python"],
        "include": ["src"],
        "exclude": [],
        "incremental": True,
        "tools": {
            "scip": {"enabled": True},
            "ast_grep": {"enabled": True},
            "ripgrep": {"enabled": True},
            "fallback_tree_sitter": {"enabled": True},
        },
    }

    rendered = module.render_resolved_config(settings)

    assert '"engine": "scip"' in rendered
    assert '"scip"' in rendered
    assert '"ast_grep"' in rendered
