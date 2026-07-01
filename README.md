# Guidelines for Agentic Development

This repository is a reusable standards pack for agentic software delivery.
It defines:

- how downstream product repositories should be structured,
- the minimum engineering requirements every project must satisfy,
- the minimum artifacts agents and humans need to collaborate safely,
- how to attach these standards to new and existing projects.

## What This Repo Is

- A guidelines repository for agentic development.
- A baseline blueprint for downstream product repositories.
- A source of minimum delivery rules for CI, CD, deployment, SonarQube, Trivy, observability, and user-visible release traceability.
- A place for reusable cross-repository helpers such as `shared-audits/`, `shared-sonar/`, `shared-trivy/`, `shared-otel/`, and `shared-code-intel/`.

## What This Repo Is Not

- Not a replacement for product-repository code, pipelines, or environment-specific runbooks.
- Not a mandate for one technology stack or one deployment platform.
- Not an excuse to add heavy process where a lighter standard is enough.

## Start Here

For most readers:

1. `Product-Repository-Blueprint.md` - downstream project structure and minimum requirements.
2. `Adoption-Guide.md` - how to attach these guidelines to new and existing repositories.
3. `shared-audits/README.md` - shared multi-scanner audit integration model.
4. `shared-sonar/README.md` - lower-level shared SonarQube runner model.
5. `shared-trivy/README.md` - lower-level shared Trivy runner model.
6. `shared-code-intel/README.md` - lower-level shared `SCIP + ast-grep + rg` code intelligence runner model.

For repository maintenance and agent work:

1. `AGENTS.md` - instruction priority and operating contract.
2. `phases-index.md` - lifecycle phase and active-role map.
3. `guidelines-index.yaml` - file ownership, dependencies, and validation contract.

## Downstream Product Baseline

Every downstream product repository should have a predictable home for:

- product requirements under `docs/requirements/`,
- architecture navigation in `docs/architecture.md`,
- technical architecture in `docs/technical-architecture.md`,
- optional ADRs and deeper architecture records under `docs/architecture/`,
- QA strategy under `docs/qa/`,
- SRE and deployment readiness under `docs/sre/`,
- implementation code under `src/`,
- automated tests under `tests/`,
- delivery automation under `.github/workflows/` and `scripts/`.

The full baseline lives in `Product-Repository-Blueprint.md`.

## Minimum Engineering Requirements

This repository expects downstream product repositories to define at least:

- an `AGENTS.md` file that points to the governing `Guidelines` baseline,
- a CI path that runs on pull requests and protected-branch pushes,
- a documented deployment path with rollback and post-deploy verification,
- a SonarQube quality gate for supported codebases,
- a Trivy security gate for filesystem scanning and, when applicable, container-image scanning,
- a mandatory code-intelligence baseline with `code-intel.py`, repo-local `code-intel/`, a `SCIP + ast-grep + rg` AST-first index path, and `docs/architecture/code-intelligence.md`,
- a persistent visible line in the UI: `Last commit: <localized date/time> | <short sha>`,
- minimum delivery artifacts covering requirements, architecture, QA, and SRE.

## Repository Map

- `requirements-standards/` - requirement standards owned by `BA` with `PO` co-ownership
- `SWE/` - engineering design and implementation standards
- `QA/` - verification and quality standards
- `SRE/` - reliability, deployment, and operations standards
- `Product-Repository-Blueprint.md` - canonical downstream repository baseline
- `Adoption-Guide.md` - rollout guidance for new and existing projects
- `guidelines/` - reusable principles, patterns, playbooks, and anti-patterns
- `shared-audits/` - reusable multi-scanner audit orchestration
- `shared-sonar/` - reusable lower-level SonarQube runner logic
- `shared-trivy/` - reusable lower-level Trivy runner logic
- `shared-otel/` - reusable Python OpenTelemetry starter pattern intended to be copied or vendored into product repositories
- `shared-code-intel/` - reusable `SCIP + ast-grep + rg` code intelligence runner logic for product repositories
- `docs/architecture.md` - simple explanation of repository layers
- `docs/architecture/code-intelligence.md` - code-intelligence baseline and downstream implementation contract
- `scripts/` - repository validation helpers
- `tests/` - regression tests for shared tooling

## Validation

Run:

```bash
npm run validate-guidelines
```

This checks indexed files, metadata on normative files, dependency references, and phase-model integrity.
