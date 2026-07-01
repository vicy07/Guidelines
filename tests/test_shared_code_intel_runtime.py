from pathlib import Path
import importlib.util
import json
import sys
import subprocess
from types import SimpleNamespace


def _load_runtime():
    module_path = Path("shared-code-intel/runtime/cli.py")
    spec = importlib.util.spec_from_file_location("shared_code_intel_runtime", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_load_index_config_reads_defaults_and_artifact_paths(tmp_path):
    module = _load_runtime()

    repo_root = tmp_path
    config_path = repo_root / "code-intel" / "config" / "index.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "\n".join(
            [
                "engine: tree-sitter",
                "languages:",
                "  - python",
                "include:",
                "  - src",
                "exclude:",
                "  - dist",
                "incremental: true",
            ]
        ),
        encoding="utf-8",
    )

    config = module.load_index_config(repo_root=repo_root, config_path=config_path)

    assert config["engine"] == "tree-sitter"
    assert config["languages"] == ["python"]
    assert config["include"] == ["src"]
    assert config["exclude"] == ["dist"]
    assert config["index_dir"] == repo_root / "code-intel" / "index"
    assert config["artifacts"]["manifest"] == repo_root / "code-intel" / "index" / "manifest.json"


def test_collect_source_files_filters_by_include_exclude_and_language(tmp_path):
    module = _load_runtime()

    repo_root = tmp_path
    (repo_root / "src").mkdir()
    (repo_root / "dist").mkdir()
    (repo_root / "src" / "main.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (repo_root / "src" / "helper.ts").write_text("export function beta() { return 2; }\n", encoding="utf-8")
    (repo_root / "dist" / "ignored.py").write_text("def ignored():\n    pass\n", encoding="utf-8")

    config = {
        "include": ["src", "dist"],
        "exclude": ["dist"],
        "languages": ["python", "typescript"],
    }

    paths = module.collect_source_files(repo_root=repo_root, config=config, changed_files=[])

    assert paths == [repo_root / "src" / "helper.ts", repo_root / "src" / "main.py"]


def test_collect_source_files_limits_to_changed_files_when_incremental_input_present(tmp_path):
    module = _load_runtime()

    repo_root = tmp_path
    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (repo_root / "src" / "helper.ts").write_text("export function beta() { return 2; }\n", encoding="utf-8")

    config = {
        "include": ["src"],
        "exclude": [],
        "languages": ["python", "typescript"],
    }

    paths = module.collect_source_files(
        repo_root=repo_root,
        config=config,
        changed_files=["src/main.py"],
    )

    assert paths == [repo_root / "src" / "main.py"]


def test_build_query_results_matches_symbols_and_files():
    module = _load_runtime()

    symbols = [
        {"id": "python:src/main.py:alpha:1", "name": "alpha", "kind": "function", "file": "src/main.py"},
        {"id": "python:src/main.py:Beta:4", "name": "Beta", "kind": "class", "file": "src/main.py"},
    ]
    files = [
        {"path": "src/main.py", "language": "python"},
        {"path": "src/other.ts", "language": "typescript"},
    ]

    results = module.build_query_results("beta", symbols=symbols, files=files)

    assert results == {
        "query": "beta",
        "symbols": [{"id": "python:src/main.py:Beta:4", "name": "Beta", "kind": "class", "file": "src/main.py"}],
        "files": [],
    }


def test_render_json_outputs_pretty_deterministic_payload():
    module = _load_runtime()

    rendered = module.render_json({"b": 2, "a": 1})

    assert json.loads(rendered) == {"a": 1, "b": 2}
    assert rendered.endswith("\n")


def test_git_commit_sha_falls_back_to_unknown_when_git_is_unavailable(tmp_path, monkeypatch):
    module = _load_runtime()

    def raise_missing_git(*args, **kwargs):
        raise FileNotFoundError("git not installed")

    monkeypatch.setattr(module.subprocess, "run", raise_missing_git)

    assert module._git_commit_sha(tmp_path) == "unknown"


def test_resolve_symbol_kind_marks_python_class_members_as_methods():
    module = _load_runtime()

    assert module.resolve_symbol_kind("python", "function_definition", parent_kind="class") == "method"
    assert module.resolve_symbol_kind("python", "function_definition", parent_kind="module") == "function"
    assert module.resolve_symbol_kind("typescript", "method_definition", parent_kind="class") == "method"


def test_build_resolved_edges_creates_contain_import_and_call_edges_for_python_graph():
    module = _load_runtime()

    symbols = [
        {"id": "python:src/main.py:<module>:1", "name": "<module>", "kind": "module", "parent_id": "", "file": "src/main.py"},
        {"id": "python:src/main.py:beta:4", "name": "beta", "kind": "function", "parent_id": "python:src/main.py:<module>:1", "file": "src/main.py"},
        {"id": "python:src/main.py:alpha:7", "name": "alpha", "kind": "function", "parent_id": "python:src/main.py:<module>:1", "file": "src/main.py"},
        {"id": "python:src/main.py:Greeter:12", "name": "Greeter", "kind": "class", "parent_id": "python:src/main.py:<module>:1", "file": "src/main.py"},
        {"id": "python:src/main.py:helper:13", "name": "helper", "kind": "method", "parent_id": "python:src/main.py:Greeter:12", "file": "src/main.py"},
        {"id": "python:src/main.py:speak:16", "name": "speak", "kind": "method", "parent_id": "python:src/main.py:Greeter:12", "file": "src/main.py"},
    ]
    import_targets = {
        "os": "external:import:os",
        "helper": "external:import:pkg.util.helper",
    }
    pending_calls = [
        {"source_id": "python:src/main.py:alpha:7", "target_name": "beta", "qualifier": "", "raw_name": "beta"},
        {"source_id": "python:src/main.py:alpha:7", "target_name": "helper", "qualifier": "", "raw_name": "helper"},
        {"source_id": "python:src/main.py:alpha:7", "target_name": "getenv", "qualifier": "os", "raw_name": "os.getenv"},
        {"source_id": "python:src/main.py:speak:16", "target_name": "helper", "qualifier": "self", "raw_name": "self.helper"},
        {"source_id": "python:src/main.py:speak:16", "target_name": "alpha", "qualifier": "", "raw_name": "alpha"},
    ]

    edges = module.build_resolved_edges(
        file_path="src/main.py",
        symbols=symbols,
        import_targets=import_targets,
        pending_calls=pending_calls,
    )

    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "python:src/main.py:beta:4", "kind": "contain", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "python:src/main.py:alpha:7", "kind": "contain", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "python:src/main.py:Greeter:12", "kind": "contain", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:Greeter:12", "target_id": "python:src/main.py:helper:13", "kind": "contain", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:Greeter:12", "target_id": "python:src/main.py:speak:16", "kind": "contain", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "external:import:os", "kind": "import", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "external:import:pkg.util.helper", "kind": "import", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:alpha:7", "target_id": "python:src/main.py:beta:4", "kind": "call", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:alpha:7", "target_id": "external:import:pkg.util.helper", "kind": "call", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:alpha:7", "target_id": "external:import:os.getenv", "kind": "call", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:speak:16", "target_id": "python:src/main.py:helper:13", "kind": "call", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:speak:16", "target_id": "python:src/main.py:alpha:7", "kind": "call", "file": "src/main.py"} in edges


def test_build_resolved_edges_creates_import_and_call_edges_for_typescript_graph():
    module = _load_runtime()

    symbols = [
        {"id": "typescript:src/main.ts:<module>:1", "name": "<module>", "kind": "module", "parent_id": "", "file": "src/main.ts"},
        {"id": "typescript:src/main.ts:alpha:2", "name": "alpha", "kind": "function", "parent_id": "typescript:src/main.ts:<module>:1", "file": "src/main.ts"},
    ]
    edges = module.build_resolved_edges(
        file_path="src/main.ts",
        symbols=symbols,
        import_targets={"beta": "external:import:./util.beta"},
        pending_calls=[{"source_id": "typescript:src/main.ts:alpha:2", "target_name": "beta", "qualifier": "", "raw_name": "beta"}],
    )

    assert {"source_id": "typescript:src/main.ts:<module>:1", "target_id": "typescript:src/main.ts:alpha:2", "kind": "contain", "file": "src/main.ts"} in edges
    assert {"source_id": "typescript:src/main.ts:<module>:1", "target_id": "external:import:./util.beta", "kind": "import", "file": "src/main.ts"} in edges
    assert {"source_id": "typescript:src/main.ts:alpha:2", "target_id": "external:import:./util.beta", "kind": "call", "file": "src/main.ts"} in edges


def test_rewrite_cross_file_edges_resolves_python_local_import_targets():
    module = _load_runtime()

    files = [
        {"path": "src/main.py", "language": "python"},
        {"path": "src/pkg/util.py", "language": "python"},
    ]
    symbols = [
        {"id": "python:src/main.py:<module>:1", "name": "<module>", "kind": "module", "parent_id": "", "file": "src/main.py"},
        {"id": "python:src/main.py:alpha:3", "name": "alpha", "kind": "function", "parent_id": "python:src/main.py:<module>:1", "file": "src/main.py"},
        {"id": "python:src/pkg/util.py:<module>:1", "name": "<module>", "kind": "module", "parent_id": "", "file": "src/pkg/util.py"},
        {"id": "python:src/pkg/util.py:helper:1", "name": "helper", "kind": "function", "parent_id": "python:src/pkg/util.py:<module>:1", "file": "src/pkg/util.py"},
    ]
    edges = [
        {"source_id": "python:src/main.py:<module>:1", "target_id": "external:import:pkg.util.helper", "kind": "import", "file": "src/main.py"},
        {"source_id": "python:src/main.py:alpha:3", "target_id": "external:import:pkg.util.helper", "kind": "call", "file": "src/main.py"},
        {"source_id": "python:src/main.py:alpha:3", "target_id": "external:import:os.getenv", "kind": "call", "file": "src/main.py"},
    ]

    rewritten = module.rewrite_cross_file_edges(files=files, symbols=symbols, edges=edges)

    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "python:src/pkg/util.py:helper:1", "kind": "import", "file": "src/main.py"} in rewritten
    assert {"source_id": "python:src/main.py:alpha:3", "target_id": "python:src/pkg/util.py:helper:1", "kind": "call", "file": "src/main.py"} in rewritten
    assert {"source_id": "python:src/main.py:alpha:3", "target_id": "external:import:os.getenv", "kind": "call", "file": "src/main.py"} in rewritten


def test_rewrite_cross_file_edges_resolves_typescript_relative_import_targets():
    module = _load_runtime()

    files = [
        {"path": "src/main.ts", "language": "typescript"},
        {"path": "src/util.ts", "language": "typescript"},
    ]
    symbols = [
        {"id": "typescript:src/main.ts:<module>:1", "name": "<module>", "kind": "module", "parent_id": "", "file": "src/main.ts"},
        {"id": "typescript:src/main.ts:alpha:2", "name": "alpha", "kind": "function", "parent_id": "typescript:src/main.ts:<module>:1", "file": "src/main.ts"},
        {"id": "typescript:src/util.ts:<module>:1", "name": "<module>", "kind": "module", "parent_id": "", "file": "src/util.ts"},
        {"id": "typescript:src/util.ts:beta:1", "name": "beta", "kind": "function", "parent_id": "typescript:src/util.ts:<module>:1", "file": "src/util.ts"},
    ]
    edges = [
        {"source_id": "typescript:src/main.ts:<module>:1", "target_id": "external:import:./util.beta", "kind": "import", "file": "src/main.ts"},
        {"source_id": "typescript:src/main.ts:alpha:2", "target_id": "external:import:./util.beta", "kind": "call", "file": "src/main.ts"},
    ]

    rewritten = module.rewrite_cross_file_edges(files=files, symbols=symbols, edges=edges)

    assert {"source_id": "typescript:src/main.ts:<module>:1", "target_id": "typescript:src/util.ts:beta:1", "kind": "import", "file": "src/main.ts"} in rewritten
    assert {"source_id": "typescript:src/main.ts:alpha:2", "target_id": "typescript:src/util.ts:beta:1", "kind": "call", "file": "src/main.ts"} in rewritten


def test_select_primary_runtime_prefers_scip_when_indexer_exists():
    module = _load_runtime()

    settings = {
        "engine": "scip",
        "languages": ["python"],
        "tools": {
            "scip": {"enabled": True, "indexers": {"python": "scip-python index"}},
            "ast_grep": {"enabled": True},
            "ripgrep": {"enabled": True},
            "fallback_tree_sitter": {"enabled": True},
        },
    }

    runtime = module.select_primary_runtime(settings)

    assert runtime == "scip"


def test_select_primary_runtime_falls_back_to_tree_sitter_without_scip_indexer():
    module = _load_runtime()

    settings = {
        "engine": "scip",
        "languages": ["python"],
        "tools": {
            "scip": {"enabled": True, "indexers": {}},
            "ast_grep": {"enabled": True},
            "ripgrep": {"enabled": True},
            "fallback_tree_sitter": {"enabled": True},
        },
    }

    runtime = module.select_primary_runtime(settings)

    assert runtime == "fallback_tree_sitter"


def test_build_chunks_from_ast_grep_matches_uses_symbol_boundaries():
    module = _load_runtime()

    symbols = [
        {
            "id": "python:src/main.py:alpha:1",
            "name": "alpha",
            "kind": "function",
            "file": "src/main.py",
            "language": "python",
            "start_point": {"row": 0, "column": 0},
            "end_point": {"row": 2, "column": 0},
        }
    ]
    ast_matches = [
        {
            "text": "def alpha():\n    return 1",
            "range": {
                "byteOffset": {"start": 0, "end": 23},
                "start": {"line": 1, "column": 1},
                "end": {"line": 2, "column": 13},
            },
            "file": "src/main.py",
        }
    ]

    chunks = module.build_chunks_from_ast_matches(symbols=symbols, ast_matches=ast_matches)

    assert chunks == [
        {
            "id": "chunk:python:src/main.py:alpha:1",
            "symbol_id": "python:src/main.py:alpha:1",
            "file": "src/main.py",
            "language": "python",
            "start_line": 1,
            "end_line": 2,
            "text": "def alpha():\n    return 1",
            "embedding": None,
        }
    ]


def test_build_chunks_from_ast_grep_matches_selects_smallest_enclosing_symbol():
    module = _load_runtime()

    symbols = [
        {
            "id": "python:src/main.py:alpha:1",
            "name": "alpha",
            "kind": "function",
            "file": "src/main.py",
            "language": "python",
            "start_point": {"row": 0, "column": 0},
            "end_point": {"row": 1, "column": 12},
        },
        {
            "id": "python:src/main.py:Beta:4",
            "name": "Beta",
            "kind": "class",
            "file": "src/main.py",
            "language": "python",
            "start_point": {"row": 3, "column": 0},
            "end_point": {"row": 6, "column": 0},
        },
    ]
    ast_matches = [
        {
            "text": "def alpha():\n    return 1",
            "range": {
                "start": {"line": 1, "column": 1},
                "end": {"line": 2, "column": 13},
            },
            "file": "src/main.py",
        },
        {
            "text": "class Beta:\n    def run(self):\n        return alpha()",
            "range": {
                "start": {"line": 4, "column": 1},
                "end": {"line": 6, "column": 23},
            },
            "file": "src/main.py",
        },
    ]

    chunks = module.build_chunks_from_ast_matches(symbols=symbols, ast_matches=ast_matches)

    assert chunks == [
        {
            "id": "chunk:python:src/main.py:alpha:1",
            "symbol_id": "python:src/main.py:alpha:1",
            "file": "src/main.py",
            "language": "python",
            "start_line": 1,
            "end_line": 2,
            "text": "def alpha():\n    return 1",
            "embedding": None,
        },
        {
            "id": "chunk:python:src/main.py:Beta:4",
            "symbol_id": "python:src/main.py:Beta:4",
            "file": "src/main.py",
            "language": "python",
            "start_line": 4,
            "end_line": 6,
            "text": "class Beta:\n    def run(self):\n        return alpha()",
            "embedding": None,
        },
    ]


def test_normalize_scip_output_builds_symbols_and_edges_from_print_json(tmp_path):
    module_path = Path("shared-code-intel/runtime/scip_adapter.py")
    spec = importlib.util.spec_from_file_location("shared_code_intel_scip_adapter", module_path)
    assert spec is not None
    assert spec.loader is not None
    scip_adapter = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scip_adapter
    spec.loader.exec_module(scip_adapter)

    repo_root = tmp_path
    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").write_text(
        "\n".join(
            [
                "from requests import get",
                "",
                "def alpha():",
                "    return get()",
                "",
            ]
        ),
        encoding="utf-8",
    )
    payload = {
        "documents": [
            {
                "language": "python",
                "relativePath": "src/main.py",
                "symbols": [
                    {
                        "symbol": "scip-python pip demo 1.0 `src/main`/alpha().",
                        "kind": "Function",
                    }
                ],
                "occurrences": [
                    {
                        "symbol": "scip-python pip demo 1.0 `src/main`/alpha().",
                        "range": [2, 0, 2, 5],
                        "symbolRoles": 1,
                    },
                    {
                        "symbol": "scip-python pip requests 2.32 `requests/get().",
                        "range": [0, 21, 0, 24],
                        "symbolRoles": 2,
                    },
                    {
                        "symbol": "scip-python pip requests 2.32 `requests/get().",
                        "range": [3, 11, 3, 14],
                        "symbolRoles": 8,
                    },
                ],
            }
        ]
    }

    files, symbols, edges = scip_adapter.normalize_scip_output(payload=payload, repo_root=repo_root)

    assert files == [
        {
            "path": "src/main.py",
            "language": "python",
            "sha256": files[0]["sha256"],
            "bytes": len((repo_root / "src" / "main.py").read_bytes()),
            "symbol_count": 2,
            "status": "indexed",
        }
    ]
    assert symbols == [
        {
            "id": "python:src/main.py:<module>:1",
            "name": "<module>",
            "kind": "module",
            "language": "python",
            "file": "src/main.py",
            "parent_id": "",
            "start_point": {"row": 0, "column": 0},
            "end_point": {"row": 4, "column": 0},
        },
        {
            "id": "python:src/main.py:alpha:3",
            "name": "alpha",
            "kind": "function",
            "language": "python",
            "file": "src/main.py",
            "parent_id": "python:src/main.py:<module>:1",
            "start_point": {"row": 2, "column": 0},
            "end_point": {"row": 2, "column": 5},
        },
    ]
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "python:src/main.py:alpha:3", "kind": "contain", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "external:scip-python pip requests 2.32 `requests/get().", "kind": "import", "file": "src/main.py"} in edges
    assert {"source_id": "python:src/main.py:alpha:3", "target_id": "external:scip-python pip requests 2.32 `requests/get().", "kind": "reference", "file": "src/main.py"} in edges


def test_normalize_scip_output_supports_symbol_roles_snake_case_from_scip_python(tmp_path):
    module_path = Path("shared-code-intel/runtime/scip_adapter.py")
    spec = importlib.util.spec_from_file_location("shared_code_intel_scip_adapter_snake_case", module_path)
    assert spec is not None
    assert spec.loader is not None
    scip_adapter = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scip_adapter
    spec.loader.exec_module(scip_adapter)

    repo_root = tmp_path
    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").write_text(
        "\n".join(
            [
                "from requests import get",
                "",
                "def alpha():",
                "    return get()",
                "",
            ]
        ),
        encoding="utf-8",
    )
    payload = {
        "documents": [
            {
                "language": "python",
                "relativePath": "src/main.py",
                "symbols": [
                    {
                        "symbol": "scip-python pip demo 1.0 `src/main`/alpha().",
                    }
                ],
                "occurrences": [
                    {
                        "symbol": "scip-python pip demo 1.0 `src/main`/alpha().",
                        "range": [2, 0, 2, 5],
                        "symbol_roles": 1,
                    },
                    {
                        "symbol": "scip-python pip requests 2.32 `requests/get().",
                        "range": [0, 21, 0, 24],
                        "symbol_roles": 2,
                    },
                    {
                        "symbol": "scip-python pip requests 2.32 `requests/get().",
                        "range": [3, 11, 3, 14],
                        "symbol_roles": 8,
                    },
                ],
            }
        ]
    }

    files, symbols, edges = scip_adapter.normalize_scip_output(payload=payload, repo_root=repo_root)

    assert files[0]["path"] == "src/main.py"
    assert any(item["id"] == "python:src/main.py:alpha:3" for item in symbols)
    assert {"source_id": "python:src/main.py:<module>:1", "target_id": "python:src/main.py:alpha:3", "kind": "contain", "file": "src/main.py"} in edges


def test_run_index_in_scip_mode_uses_normalized_scip_symbols_and_ast_grep_chunks(tmp_path, monkeypatch):
    module = _load_runtime()

    repo_root = tmp_path
    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

    config = {
        "engine": "scip",
        "languages": ["python"],
        "include": ["src"],
        "exclude": [],
        "incremental": True,
        "index_dir": repo_root / "code-intel" / "index",
        "artifacts": module.build_artifact_paths(repo_root / "code-intel" / "index"),
        "tools": {
            "scip": {"enabled": True, "indexers": {"python": "scip-python index"}},
            "ast_grep": {"enabled": True},
            "ripgrep": {"enabled": True},
            "fallback_tree_sitter": {"enabled": True},
        },
        "raw_artifacts": {
            "scip": repo_root / "code-intel" / "index" / "scip",
            "ast_grep": repo_root / "code-intel" / "index" / "ast-grep",
        },
    }

    def fake_run_scip_index(command, repo_root, output_path):
        del command, repo_root
        output_path.write_text("raw", encoding="utf-8")
        return 0

    def fake_load_runtime_module(module_filename: str, module_name: str):
        if module_filename == "scip_adapter.py":
            return SimpleNamespace(
                run_scip_index=fake_run_scip_index,
                load_scip_json=lambda output_path, repo_root: {
                    "documents": [
                        {
                            "language": "python",
                            "relativePath": "src/main.py",
                            "symbols": [
                                {"symbol": "scip-python pip demo 1.0 `src/main`/alpha().", "kind": "Function"}
                            ],
                            "occurrences": [
                                {
                                    "symbol": "scip-python pip demo 1.0 `src/main`/alpha().",
                                    "range": [0, 0, 0, 5],
                                    "symbolRoles": 1,
                                }
                            ],
                        }
                    ]
                },
                normalize_scip_output=lambda payload, repo_root: (
                    [
                        {
                            "path": "src/main.py",
                            "language": "python",
                            "sha256": "abc",
                            "bytes": 26,
                            "symbol_count": 2,
                            "status": "indexed",
                        }
                    ],
                    [
                        {
                            "id": "python:src/main.py:<module>:1",
                            "name": "<module>",
                            "kind": "module",
                            "language": "python",
                            "file": "src/main.py",
                            "parent_id": "",
                            "start_point": {"row": 0, "column": 0},
                            "end_point": {"row": 1, "column": 12},
                        },
                        {
                            "id": "python:src/main.py:alpha:1",
                            "name": "alpha",
                            "kind": "function",
                            "language": "python",
                            "file": "src/main.py",
                            "parent_id": "python:src/main.py:<module>:1",
                            "start_point": {"row": 0, "column": 0},
                            "end_point": {"row": 1, "column": 12},
                        },
                    ],
                    [
                        {
                            "source_id": "python:src/main.py:<module>:1",
                            "target_id": "python:src/main.py:alpha:1",
                            "kind": "contain",
                            "file": "src/main.py",
                        }
                    ],
                ),
            )
        if module_filename == "ast_grep_adapter.py":
            return SimpleNamespace(
                run_ast_grep_scan=lambda repo_root, pattern, language: [
                    {
                        "text": "def alpha():\n    return 1",
                        "range": {
                            "start": {"line": 1, "column": 1},
                            "end": {"line": 2, "column": 13},
                        },
                        "file": "src/main.py",
                    }
                ]
            )
        raise AssertionError(module_filename)

    monkeypatch.setattr(module, "_load_runtime_module", fake_load_runtime_module)

    manifest = module.run_index(repo_root=repo_root, config=config, changed_files=[])
    chunks = json.loads(config["artifacts"]["chunks"].read_text(encoding="utf-8"))

    assert manifest["counts"] == {"files": 1, "symbols": 2, "edges": 1, "chunks": 1}
    assert chunks == [
        {
            "id": "chunk:python:src/main.py:alpha:1",
            "symbol_id": "python:src/main.py:alpha:1",
            "file": "src/main.py",
            "language": "python",
            "start_line": 1,
            "end_line": 2,
            "text": "def alpha():\n    return 1",
            "embedding": None,
        }
    ]
