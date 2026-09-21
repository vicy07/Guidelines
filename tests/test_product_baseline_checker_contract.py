from pathlib import Path


def test_baseline_template_pins_both_repositories():
    template = Path("templates/governance-baseline.yaml").read_text(encoding="utf-8")

    assert "https://github.com/vicy07/Guidelines" in template
    assert "https://github.com/vicy07/AI-Governance" in template
    assert template.count("REPLACE_WITH_FULL_COMMIT_SHA") == 2


def test_checker_covers_dual_references_revisions_and_docs():
    checker = Path("scripts/check-product-baseline.mjs").read_text(encoding="utf-8")

    assert "AGENTS.md missing reference" in checker
    assert "40-character commit SHA" in checker
    assert "docs/technical-architecture.md" in checker
    assert 'args.includes("--strict")' in checker
