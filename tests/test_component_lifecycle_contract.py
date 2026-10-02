from pathlib import Path


def test_component_lifecycle_standard_is_indexed_and_consumed():
    index = Path("guidelines-index.yaml").read_text(encoding="utf-8")
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")

    assert "Areas/swe/component-lifecycle-guidelines.md" in index
    assert "audits/sbom/components.cdx.json" in blueprint
    assert "python audits.py components check" in blueprint
    assert "audits/config/components.yaml" in adoption


def test_component_lifecycle_standard_has_required_coverage_and_gates():
    standard = Path("Areas/swe/component-lifecycle-guidelines.md").read_text(encoding="utf-8")

    for required in (
        "direct and transitive libraries",
        "third-party",
        "first-party architectural components",
        "license expression using valid SPDX identifiers or expressions",
        "license type: `permissive`",
        "License Compatibility and Risk",
        "before a component or architecture option is approved",
        "incompatible license combinations",
        "Criticality Classification",
        "Lifecycle Exposure",
        "Component criticality \\ Lifecycle exposure",
        "Scheduled monitoring must run at least weekly",
        "Evidence not available",
    ):
        assert required in standard


def test_license_review_starts_at_architecture_and_flows_to_sbom():
    requirements_architecture = Path(
        "Areas/requirements/architecture-standard.md"
    ).read_text(encoding="utf-8")
    engineering_architecture = Path(
        "Areas/swe/architecture-guidelines.md"
    ).read_text(encoding="utf-8")
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")

    assert "before they are approved for implementation" in requirements_architecture
    assert "Before approving a component or architecture option" in engineering_architecture
    assert "license expression/value" in blueprint
    assert "License compatibility must be assessed during architecture design" in blueprint
