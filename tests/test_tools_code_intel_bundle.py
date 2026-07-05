from pathlib import Path


def test_dockerfile_exposes_runtime_package_on_pythonpath():
    dockerfile = Path("Tools/code-intel/Dockerfile").read_text(encoding="utf-8")

    assert "PYTHONPATH=/opt/code-intel" in dockerfile


def test_readme_mentions_scip_ast_grep_and_ripgrep_as_primary_stack():
    readme = Path("Tools/code-intel/README.md").read_text(encoding="utf-8")

    assert "SCIP" in readme
    assert "ast-grep" in readme
    assert "rg" in readme


def test_dockerfile_installs_ast_grep_and_ripgrep():
    dockerfile = Path("Tools/code-intel/Dockerfile").read_text(encoding="utf-8")

    assert "ripgrep" in dockerfile
    assert "ast-grep" in dockerfile


def test_dockerfile_installs_scip_cli():
    dockerfile = Path("Tools/code-intel/Dockerfile").read_text(encoding="utf-8")

    assert "SCIP_VERSION" in dockerfile
    assert "scip --help" in dockerfile or "scip --version" in dockerfile
    assert "github.com/scip-code/scip/releases/download" in dockerfile


def test_readme_mentions_scip_cli_and_print_json_path():
    readme = Path("Tools/code-intel/README.md").read_text(encoding="utf-8")

    assert "scip print --json" in readme
    assert "scip v0.9.0" in readme


def test_dockerfile_exposes_optional_indexers_target_for_python_and_typescript():
    dockerfile = Path("Tools/code-intel/Dockerfile").read_text(encoding="utf-8")

    assert "FROM node:20-bookworm-slim AS node-runtime" in dockerfile
    assert "FROM runtime AS indexers" in dockerfile
    assert "@sourcegraph/scip-python" in dockerfile
    assert "@sourcegraph/scip-typescript" in dockerfile


def test_readme_mentions_optional_indexers_target_and_node20_profile():
    readme = Path("Tools/code-intel/README.md").read_text(encoding="utf-8")

    assert "docker build --target indexers" in readme
    assert "Node 20" in readme
    assert "scip-python" in readme
    assert "scip-typescript" in readme


def test_dockerfile_exposes_optional_jvm_dotnet_target_for_java_and_csharp():
    dockerfile = Path("Tools/code-intel/Dockerfile").read_text(encoding="utf-8")

    assert "FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet-runtime" in dockerfile
    assert "FROM eclipse-temurin:17-jdk AS java-runtime" in dockerfile
    assert "FROM runtime AS indexers-jvm-dotnet" in dockerfile
    assert "COPY --from=java-runtime" in dockerfile
    assert "dotnet tool install --global scip-dotnet" in dockerfile
    assert "scip-java_2.13" in dockerfile


def test_readme_mentions_optional_jvm_dotnet_target_and_java_csharp_profile():
    readme = Path("Tools/code-intel/README.md").read_text(encoding="utf-8")

    assert "docker build --target indexers-jvm-dotnet" in readme
    assert "Java 17" in readme
    assert ".NET 8" in readme
    assert "scip-java" in readme
    assert "scip-dotnet" in readme


def test_baseline_docs_require_generated_code_intel_artifacts_to_stay_out_of_git():
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")
    architecture = Path("docs/architecture/code-intelligence.md").read_text(encoding="utf-8")

    assert "must not be committed to git" in blueprint
    assert "ignore `code-intel/index/`" in blueprint
    assert "must not be committed to git" in adoption
    assert "must not be committed to git" in architecture


def test_baseline_docs_require_minimal_downstream_rollout_surface():
    adoption = Path("Adoption-Guide.md").read_text(encoding="utf-8")
    architecture = Path("docs/architecture/code-intelligence.md").read_text(encoding="utf-8")

    assert "narrowest practical repo-local surface" in adoption
    assert "Do not expand the main README, docs index, or repo-wide tests" in adoption
    assert "Do not add extra downstream docs, tests, or planning artifacts" in architecture


def test_downstream_code_intelligence_document_content_contract_lives_in_requirements():
    requirement = Path("Areas/requirements/code-intelligence-standard.md").read_text(encoding="utf-8")
    architecture = Path("docs/architecture/code-intelligence.md").read_text(encoding="utf-8")
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")

    assert "Required Sections" in requirement
    assert "Purpose and Scope" in requirement
    assert "Local Control Surface" in requirement
    assert "Git and Retention Policy" in requirement
    assert "Areas/requirements/code-intelligence-standard.md" in architecture
    assert "Areas/requirements/code-intelligence-standard.md" in blueprint


def test_downstream_architecture_document_content_contract_lives_in_requirements():
    requirement = Path("Areas/requirements/architecture-standard.md").read_text(encoding="utf-8")
    architecture = Path("docs/architecture.md").read_text(encoding="utf-8")
    blueprint = Path("Product-Repository-Blueprint.md").read_text(encoding="utf-8")

    assert "Required Sections" in requirement
    assert "Repository Architecture Map" in requirement
    assert "Cross-References to Detailed Design" in requirement
    assert "Areas/requirements/architecture-standard.md" in architecture
    assert "Areas/requirements/architecture-standard.md" in blueprint
