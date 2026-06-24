# Adoption Guide

## Purpose

Explain how to attach this guidelines repository to new and existing product repositories with the least disruptive path that still creates a usable agentic-development baseline.

## Recommended Adoption Model

Use one of two tracks:

1. New project bootstrap
2. Existing project retrofit

Do not force the same rollout shape on both.

## Track 1: New Project Bootstrap

For a new repository:

1. Create the target structure from `Product-Repository-Blueprint.md`.
2. Add `AGENTS.md`, `Repository.md`, `phases-index.md`, and `guidelines-index.yaml`.
3. Create the minimum artifact set under `docs/requirements/`, `docs/`, `docs/qa/`, and `docs/sre/`.
4. Add `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`.
5. Add `sonar-project.properties` and a thin `sonar.py` wrapper that reuses `shared-sonar/sonar_runner.py`.
6. Add the repository observability stack and OTLP contract.
7. Implement the visible line `Last commit: <localized date/time> | <short sha>` in the product UI if the product is user-facing.

This is the preferred path because it avoids later migration overhead.

## Track 2: Existing Project Retrofit

For an existing repository, do not rewrite the whole structure unless the current layout is already failing delivery.

Recommended sequence:

1. Inventory current docs, tests, workflows, and deployment scripts.
2. Map existing files to the target baseline before creating new ones.
3. Add only the missing minimum artifacts.
4. Normalize CI, deploy, SonarQube, and observability gates before attempting broader documentation cleanup.
5. When a compliance audit is run, create `docs/audits/` and save the audit findings there, including the exact `Guidelines` version pinned by commit hash and commit date.
6. Add the visible last-commit line without changing unrelated architecture.
7. Move toward the target structure incrementally as files are naturally touched.

## Practical Proposal for Existing Projects

Use a three-step rollout:

### Step 1: Control Surface

Add:

- `AGENTS.md`
- `phases-index.md`
- `guidelines-index.yaml`
- a short `Repository.md`

Outcome:

- agents can navigate the repo deterministically,
- role ownership and file discovery stop being implicit.

### Step 2: Delivery Gates

Add or normalize:

- CI workflow,
- deploy workflow or release workflow,
- SonarQube integration,
- observability stack with OTLP contract,
- minimum smoke and regression checks.

Outcome:

- changes are gated before merge and release,
- repository health stops depending on manual memory.

### Step 3: Minimal Artifacts

Create or align:

- `docs/requirements/mission.md`
- `docs/requirements/use-cases.md`
- `docs/requirements/user-flows.md`
- `docs/architecture.md`
- `docs/technical-architecture.md`
- `docs/qa/test-strategy.md`
- `docs/sre/deployment-and-operations.md`

Outcome:

- agents and humans share the same minimum context for delivery decisions.

Architecture documentation rule:

- keep `docs/architecture.md` short and navigational,
- keep `docs/technical-architecture.md` as the canonical technical design document,
- use `docs/architecture/` only for ADRs or deeper supporting architecture records when needed.

## Integration Rules

- Reuse existing code and workflow conventions where they are already effective.
- Do not rename stable directories just to match the blueprint if a mapping layer is enough.
- Prefer wrappers over copied shared logic for SonarQube integration.
- If evidence for a rule is missing, document `Evidence not available` instead of inventing compliance.

## Suggested Consumption Pattern

The lightest workable integration for most teams is:

1. Copy the governance files.
2. Create the minimal docs set.
3. Wire CI and deploy workflows.
4. Reuse `shared-sonar/`.
5. Define OTEL env vars and the repository observability path. Python repositories can copy or vendor `shared-otel/telemetry.py` and keep a thin local wrapper for framework instrumentation.
6. If a compliance audit is performed, create `docs/audits/` and save the audit output with the `Guidelines` commit hash and commit date used for the review.
7. Add the visible last-commit line.

That gives a usable baseline without forcing a full repository redesign on day one.
