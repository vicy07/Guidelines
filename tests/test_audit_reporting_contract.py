from pathlib import Path


def test_audit_reporting_standard_is_indexed_and_consumed():
    index = Path("guidelines-index.yaml").read_text(encoding="utf-8")
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")
    playbooks = Path("guidelines/playbooks/README.md").read_text(encoding="utf-8")

    standard_path = "guidelines/playbooks/audit-reporting-standard.md"
    assert standard_path in index
    assert standard_path in blueprint
    assert standard_path in adoption
    assert "audit-reporting-standard.md" in playbooks


def test_audit_reporting_standard_requires_one_file_and_complete_coverage():
    standard = Path("guidelines/playbooks/audit-reporting-standard.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "exactly one consolidated",
        "Repository-wide audit execution is opt-in",
        "must not implicitly start the full audit suite",
        "Audit Operator",
        "does not own or",
        "repository-wide audit by default",
        "docs/audits/",
        "YYYY-MM-DD-<scope>.md",
        "EOL and component lifecycle",
        "Trivy filesystem scan",
        "Trivy image scan",
        "Security review",
        "GDPR and privacy review",
        "`tool/runner`",
        "`AI review`",
        "`not-run`",
        "`not-applicable`",
        "Evidence not available",
        "must not claim legal certification",
    ):
        assert required in standard
