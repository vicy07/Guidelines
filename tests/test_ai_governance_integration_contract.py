from pathlib import Path


AI_GOVERNANCE_URL = "https://github.com/vicy07/AI-Governance"


def test_primary_adoption_documents_reference_ai_governance():
    for path in (
        "README.md",
        "AGENTS.md",
        "Adoption-Guide.md",
        "Product-Repository-Blueprint.md",
    ):
        assert AI_GOVERNANCE_URL in Path(path).read_text(encoding="utf-8")


def test_adoption_guide_provides_dual_baseline_agents_template():
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")

    assert "## Root AGENTS Reference Template" in adoption
    assert "https://github.com/vicy07/Guidelines" in adoption
    assert "Adopted Guidelines revision: <commit SHA>" in adoption
