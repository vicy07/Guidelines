# Product Repository Blueprint (Agentic Mode)

## Purpose

Define the recommended baseline structure for downstream software product repositories that consume these guidelines.

## Scope Boundary

- This document describes target product repositories.
- It does not describe the physical structure of this guidelines repository.

## Proven Production Baseline

For a production solution repository, keep role artifacts under `docs/` and keep delivery code/tests in `src/` and `tests/`.

## Required Root Structure

```text
<project-repo>/
  docs/
    requirements/
      mission.md
      use-cases.md
      user-flow.md
      nfr.md
    architecture/
      adr/
      system-design.md
    qa/
      test-strategy.md
      test-matrix.md
    sre/
      slo-sli.md
      runbooks/
      incident-playbook.md
  src/
  tests/
    unit/
    integration/
    e2e/
    regression/
    performance/
    security/
  scripts/
  .github/
  README.md
  Repository.md
  AGENTS.md
  phases-index.md
  guidelines-index.yaml
```

## Top-Level Ownership Model

- `docs/requirements/` - product behavior source of truth for the target solution.
- `docs/architecture/` - engineering architecture, implementation boundaries, and security design decisions (`SWE` ownership).
- `docs/qa/` - test strategy and verification planning (`QA` ownership).
- `docs/sre/` - reliability, operability, and incident readiness standards (`SRE` ownership).
- `src/` - implementation code owned primarily by `SWE`.
- `tests/` - automated and manual test assets organized by testing phase/type, owned by `QA` and `SWE`.

## Role Model (Recommended)

- Core delivery roles for most software repositories: `PO`, `BA`, `SWE`, `QA`, `SRE`.
- `PO` and `BA` own problem framing, scope boundaries, and acceptance intent.
- `SWE` owns architecture and implementation outcomes.
- `QA` owns verification strategy and quality evidence.
- `SRE` owns runtime reliability, operability, and incident readiness.
- Role boundaries must remain explicit in docs and phase outputs.

## Role Docs Consolidation Rule

- In product repositories, do not create parallel top-level role folders like `Requirements/`, `SWE/`, `QA/`, `SRE/`.
- Consolidate role guidance in `docs/requirements`, `docs/architecture`, `docs/qa`, and `docs/sre`.
- Keep role-accountability boundaries explicit inside each document.

## Code and Test Placement Rules

- `SWE` stores production code in `src/`.
- `QA` and `SWE` store test assets in `tests/` subfolders by test phase/type.
- The selected test folder model (`unit/integration/e2e/regression/performance/security`) must be reflected in the project test strategy.
- Cross-role boundary note:
  - `SWE` is accountable for application code and testability hooks.
  - `QA` is accountable for functional/regression verification content.
  - `SRE` is accountable for runtime reliability controls and incident readiness, outside the `tests/` ownership boundary.

## Core Document Rules (Recommended)

- Required product-level document set:
  - `docs/requirements/mission.md`
  - `docs/requirements/use-cases.md`
  - `docs/requirements/user-flow.md`
  - `docs/architecture/system-design.md`
  - `docs/qa/test-strategy.md`
  - `docs/sre/slo-sli.md`
- Each normative document should include metadata fields: `Version`, `Owner`, `Last Updated`.
- Every requirement-level statement should be testable and traceable to at least one verification asset in `tests/` or QA docs.
- Architecture decisions with non-trivial tradeoffs should be captured in `docs/architecture/adr/`.
- Reliability goals in `docs/sre/` should be linked to runtime signals (metrics/logs/traces) and release gates.

## SRE Operating Rules (Recommended)

- Own service reliability standards: SLO/SLI definitions, error budgets, and alert quality criteria.
- Define runtime safeguards: health checks, graceful degradation, rollout/rollback guardrails.
- Own incident process: on-call readiness, severity model, response playbooks, and post-incident follow-up.
- Require observability baseline in production: logs, metrics, traces, and actionable dashboards.
- Define release reliability gates with `SWE` and `QA`: canary criteria, rollback triggers, and operational sign-off.

## Definition of Ready (New Product Repository)

A new product repository is ready for agentic delivery when:
- The root structure matches this blueprint.
- `src/` and `tests/` are present and used as primary implementation/verification locations.
- `docs/requirements`, `docs/architecture`, `docs/qa`, and `docs/sre` exist with clear ownership.
- `phases-index.md` exists and maps phases to active roles.
- `guidelines-index.yaml` references valid files and dependencies.
- Normative files include required metadata fields (`Version`, `Owner`, `Last Updated`).
- Validation pipeline passes (for example, `npm run validate-guidelines` when configured).
