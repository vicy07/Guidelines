"""Behavioral coverage for explicit adoption and legacy structural checks."""

import json
import subprocess
from pathlib import Path

import pytest


CHECKER = Path("scripts/check-product-baseline.mjs").resolve()
PRODUCT_DOCS = (
    "docs/requirements/mission.md",
    "docs/requirements/use-cases.md",
    "docs/requirements/user-flows.md",
    "docs/architecture.md",
    "docs/technical-architecture.md",
    "docs/architecture/code-intelligence.md",
    "docs/qa/test-strategy.md",
    "docs/sre/deployment-and-operations.md",
)


def write(root, relative, content="# Evidence\n"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_repo(root, *, profile=None, mode="basic", product_docs=True):
    write(root, "AGENTS.md", "\n".join((
        "https://github.com/vicy07/Guidelines",
        "https://github.com/vicy07/AI-Governance",
    )))
    write(root, "README.md")
    baseline = {
        "version": 1,
        "guidelines": {"revision": "a" * 40},
        "ai_governance": {"revision": "b" * 40},
    }
    if profile is not None:
        baseline["adoption"] = {
            "profile": profile,
            "code_intelligence": mode,
            "owner": "product-engineering",
            "rationale": "Finite CLI; language navigation covers current impact analysis.",
        }
    write(root, ".governance/baseline.yaml", json.dumps(baseline))
    if product_docs:
        for doc in PRODUCT_DOCS:
            write(root, doc)
    return baseline


def check(root, *, strict=True):
    args = ["node", str(CHECKER), str(root)]
    if strict:
        args.append("--strict")
    return subprocess.run(args, capture_output=True, text=True, check=False)


@pytest.mark.parametrize("profile", ["library-cli", "service-web", "critical-system"])
def test_basic_product_needs_no_custom_index(tmp_path, profile):
    make_repo(tmp_path, profile=profile)
    result = check(tmp_path)
    assert result.returncode == 0, result.stderr
    assert f"{profile}/basic" in result.stdout
    assert not (tmp_path / "code-intel.py").exists()


def test_docs_only_uses_readme_instead_of_product_scaffolding(tmp_path):
    make_repo(tmp_path, profile="docs-only", product_docs=False)
    assert check(tmp_path).returncode == 0
    (tmp_path / "README.md").unlink()
    result = check(tmp_path)
    assert result.returncode == 1
    assert "missing: README.md" in result.stderr


def test_indexed_mode_requires_static_integration_but_not_generated_artifacts(tmp_path):
    make_repo(tmp_path, profile="service-web", mode="indexed")
    result = check(tmp_path)
    assert result.returncode == 1
    assert "missing: code-intel.py" in result.stderr
    assert "missing: code-intel/config/index.yaml" in result.stderr
    write(tmp_path, "code-intel.py", "# local index entrypoint\n")
    write(tmp_path, "code-intel/config/index.yaml", "engine: scip\n")
    assert check(tmp_path).returncode == 0
    assert not (tmp_path / "code-intel/index").exists()


def test_indexed_docs_only_still_requires_index_documentation(tmp_path):
    make_repo(tmp_path, profile="docs-only", mode="indexed", product_docs=False)
    write(tmp_path, "code-intel.py")
    write(tmp_path, "code-intel/config/index.yaml")
    result = check(tmp_path)
    assert result.returncode == 1
    assert "missing: docs/architecture/code-intelligence.md" in result.stderr
    write(tmp_path, "docs/architecture/code-intelligence.md")
    assert check(tmp_path).returncode == 0


def test_legacy_keeps_eight_document_check(tmp_path):
    make_repo(tmp_path)
    assert "legacy document set" in check(tmp_path).stdout
    (tmp_path / PRODUCT_DOCS[-1]).unlink()
    result = check(tmp_path)
    assert result.returncode == 1
    assert PRODUCT_DOCS[-1] in result.stderr


@pytest.mark.parametrize("adoption", [
    None, [], "docs-only", {},
    {"profile": "doc-only", "code_intelligence": "basic"},
    {"profile": "docs-only", "code_intelligence": "off"},
    {"profile": "docs-only", "code_intelligence": "basic", "owner": " ", "rationale": "ok"},
    {"profile": "docs-only", "code_intelligence": "basic", "owner": "SWE", "rationale": 5},
    {"profile": "docs-only", "code_intelligence": "basic", "owner": "REPLACE_WITH_TEAM", "rationale": "ok"},
])
def test_invalid_adoption_never_silently_passes(tmp_path, adoption):
    baseline = make_repo(tmp_path, product_docs=False)
    baseline["adoption"] = adoption
    write(tmp_path, ".governance/baseline.yaml", json.dumps(baseline))
    result = check(tmp_path)
    assert result.returncode == 1
    assert "adoption" in result.stderr
    report = check(tmp_path, strict=False)
    assert report.returncode == 0
    assert "GAP:" in report.stderr
    assert "OK:" not in report.stdout


@pytest.mark.parametrize("bad_revision", ["main", "REPLACE_WITH_FULL_COMMIT_SHA", "", None])
def test_profile_cannot_bypass_revision_pins(tmp_path, bad_revision):
    baseline = make_repo(tmp_path, profile="docs-only", product_docs=False)
    baseline["guidelines"]["revision"] = bad_revision
    write(tmp_path, ".governance/baseline.yaml", json.dumps(baseline))
    result = check(tmp_path)
    assert result.returncode == 1
    assert "guidelines.revision" in result.stderr


@pytest.mark.parametrize("content", ["", "[not: valid", "just text", "[]"])
def test_empty_or_invalid_lock_file_cannot_pass(tmp_path, content):
    make_repo(tmp_path)
    write(tmp_path, ".governance/baseline.yaml", content)
    assert check(tmp_path).returncode == 1


def test_empty_agents_file_cannot_bypass_dual_references(tmp_path):
    make_repo(tmp_path, profile="docs-only", product_docs=False)
    write(tmp_path, "AGENTS.md", "")
    result = check(tmp_path)
    assert result.returncode == 1
    assert result.stderr.count("AGENTS.md missing reference") == 2


def test_directory_is_not_a_required_document(tmp_path):
    make_repo(tmp_path, profile="docs-only", product_docs=False)
    (tmp_path / "README.md").unlink()
    (tmp_path / "README.md").mkdir()
    result = check(tmp_path)
    assert result.returncode == 1
    assert "missing: README.md" in result.stderr
    assert "EISDIR" not in result.stderr
