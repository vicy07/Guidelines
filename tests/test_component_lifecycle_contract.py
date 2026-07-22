from pathlib import Path


def test_component_lifecycle_standard_is_indexed_and_consumed():
    index = Path("guidelines-index.yaml").read_text(encoding="utf-8")
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")

    assert "Areas/swe/component-lifecycle-guidelines.md" in index
    assert "audits/sbom/components.cdx.json" in blueprint
    assert "python audits.py eol check" in blueprint
    assert "audits/config/eol.yaml" in adoption


def test_component_lifecycle_standard_has_required_coverage_and_gates():
    standard = Path("Areas/swe/component-lifecycle-guidelines.md").read_text(encoding="utf-8")

    for required in (
        "direct and transitive libraries",
        "third-party",
        "first-party architectural components",
        "Criticality Classification",
        "Lifecycle Exposure",
        "Component criticality \\ Lifecycle exposure",
        "Scheduled monitoring must run at least weekly",
        "Evidence not available",
    ):
        assert required in standard
