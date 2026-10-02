from pathlib import Path


def test_release_notes_contract_covers_source_matched_web_delivery():
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")

    for required in (
        "### Release Notes Contract",
        "docs/releases/",
        "X.Y.Z.md",
        "final notes must be reviewed",
        "before the CI\nartifact is built",
        "release-notes page",
        "primary navigation",
        "persistent footer/status line",
        "SWE owns source generation",
        "UX\nowns accessible page structure",
        "QA verifies",
        "SRE verifies",
    ):
        assert required in blueprint

    assert "Add reviewed `docs/releases/X.Y.Z.md` files to the release workflow." in adoption
    assert "primary navigation or the required footer/status line" in adoption


def test_ux_and_implementation_standards_require_a_discoverable_web_link():
    ux = Path("Areas/ux/ui-ux-guidelines-standard.md").read_text(encoding="utf-8")
    implementation = Path("Areas/swe/implementation-guidelines.md").read_text(
        encoding="utf-8"
    )

    assert "release-notes page" in ux
    assert "primary-navigation link or a link placed with the required persistent footer/status line" in ux
    assert "release-notes page" in implementation
    assert "primary navigation or the required persistent footer/status line" in implementation
