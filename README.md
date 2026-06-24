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
- A source of minimum delivery rules for CI, CD, deployment, SonarQube, and user-visible release traceability.
- A place for reusable cross-repository helpers such as `shared-sonar/`.

## What This Repo Is Not

- Not a replacement for product-repository code, pipelines, or environment-specific runbooks.
- Not a mandate for one technology stack or one deployment platform.
- Not an excuse to add heavy process where a lighter standard is enough.

## Start Here

For most readers:

1. `Product-Repository-Blueprint.md` - downstream project structure and minimum requirements.
2. `Adoption-Guide.md` - how to attach these guidelines to new and existing repositories.
3. `shared-sonar/README.md` - shared SonarQube integration model.

For repository maintenance and agent work:

1. `AGENTS.md` - instruction priority and operating contract.
2. `phases-index.md` - lifecycle phase and active-role map.
3. `guidelines-index.yaml` - file ownership, dependencies, and validation contract.

## Downstream Product Baseline

Every downstream product repository should have a predictable home for:

- product requirements under `docs/requirements/`,
- architecture decisions under `docs/architecture/`,
- QA strategy under `docs/qa/`,
- SRE and deployment readiness under `docs/sre/`,
- implementation code under `src/`,
- automated tests under `tests/`,
- delivery automation under `.github/workflows/` and `scripts/`.

The full baseline lives in `Product-Repository-Blueprint.md`.

## Minimum Engineering Requirements

This repository expects downstream product repositories to define at least:

- a CI path that runs on pull requests and protected-branch pushes,
- a documented deployment path with rollback and post-deploy verification,
- a SonarQube quality gate for supported codebases,
- a persistent visible line in the UI: `Last commit: <localized date/time> | <short sha>`,
- minimum delivery artifacts covering requirements, architecture, QA, and SRE.

## Repository Map

- `Requirements/` - requirement standards owned by `BA` with `PO` co-ownership
- `SWE/` - engineering design and implementation standards
- `QA/` - verification and quality standards
- `SRE/` - reliability, deployment, and operations standards
- `Product-Repository-Blueprint.md` - canonical downstream repository baseline
- `Adoption-Guide.md` - rollout guidance for new and existing projects
- `guidelines/` - reusable principles, patterns, playbooks, and anti-patterns
- `shared-sonar/` - reusable SonarQube runner logic
- `shared-otel/` - reusable Python OpenTelemetry starter pattern intended to be copied or vendored into product repositories
- `docs/architecture.md` - simple explanation of repository layers
- `scripts/` - repository validation helpers
- `tests/` - regression tests for shared tooling

## Validation

Run:

```bash
npm run validate-guidelines
```

This checks indexed files, metadata on normative files, dependency references, and phase-model integrity.
