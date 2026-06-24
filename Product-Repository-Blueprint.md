# Product Repository Blueprint (Agentic Development Baseline)

## Purpose

Define the minimum recommended baseline for downstream software product repositories that want predictable agentic delivery without forcing a specific stack.

## Design Rules

- Keep the baseline small enough to adopt in real projects.
- Preserve the product repository's chosen language, framework, and deployment platform.
- Standardize only the parts that improve agent and human coordination.
- Prefer incremental adoption over big-bang repository rewrites.

## Required Root Structure

```text
<project-repo>/
  docs/
    requirements/
      mission.md
      use-cases.md
      user-flows.md
    architecture/
      system-design.md
      adr/
    qa/
      test-strategy.md
    sre/
      deployment-and-operations.md
  src/
  tests/
    unit/
    integration/
    e2e/
  scripts/
  .github/
    workflows/
      ci.yml
      deploy.yml
  README.md
  Repository.md
  AGENTS.md
  phases-index.md
  guidelines-index.yaml
  sonar-project.properties
  sonar.py
```

## Structure Rules

- `docs/requirements/` is the product behavior source of truth.
- `docs/architecture/` captures system boundaries and non-trivial technical decisions.
- `docs/qa/` captures how the project proves quality.
- `docs/sre/` captures how the project is deployed, observed, rolled back, and operated.
- `src/` contains implementation code.
- `tests/` contains automated verification assets organized by test level.
- `.github/workflows/` contains delivery automation that enforces minimum quality gates.

## Minimum Delivery Requirements

### 1. CI

Every project must define a CI workflow that:

- runs on pull requests and protected-branch pushes,
- installs dependencies deterministically,
- runs the fastest meaningful automated checks for the repository,
- runs at least a smoke regression set before merge,
- fails the build on test or quality-gate failure.

Minimum CI outcome:

- the repository can prove that a change was built and checked before merge,
- the result is visible in pull requests and branch history.

### 2. CD and Deployment

Every deployable project must define a deployment path that includes:

- a documented target environment model,
- one command or workflow per deploy path,
- post-deploy verification,
- rollback or roll-forward guidance,
- ownership of deployment approval and runtime checks.

If a repository is a library and is not deployed as a runtime service, replace deployment guidance with a documented release/publish flow.

### 3. SonarQube

Every supported codebase must provide:

- `sonar-project.properties`,
- a thin local `sonar.py` wrapper,
- coverage report generation wired into the Sonar run,
- a required quality gate for `main` and release branches.

Recommended integration model:

1. Keep project-specific config in the product repo.
2. Reuse shared logic from this repository's `shared-sonar/sonar_runner.py`.
3. Fail the check if the SonarQube quality gate is not `OK`.

### 4. Visible Release Traceability

Every user-facing solution must render a persistent visible line:

`Last commit: <localized date/time> | <short sha>`

If commit details are unavailable, the UI must still render:

`Last commit: unavailable`

This requirement defines the visible product outcome, not the implementation mechanism.
The visible line must resolve correctly in deployed environments too, not only in local development.

### 5. Observability Stack

Every downstream repository must define an observability stack.

Universal minimum:

- structured logs,
- operational metrics,
- distributed tracing through OpenTelemetry,
- a documented OTLP configuration contract,
- stable service or application attribution for emitted telemetry.

Observability implementation rule:

- the product repository owns its runtime wiring,
- shared helpers may be reused as starter patterns,
- long-lived runtime dependence on this `Guidelines` repository is not the target state.

Minimum OTLP contract:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

Repository-type expectations:

- Backend and service repositories must emit traces, metrics, and logs from the running service and document the active OTLP export path.
- Frontend or static-web repositories must emit client telemetry and error events through a documented path that can be correlated with the wider observability stack.
- Library and CLI repositories must emit structured logs and define how OpenTelemetry attribution and export are enabled when the component runs directly or inside a host runtime.

Recommended reuse model:

- Python repositories can copy or vendor `shared-otel/telemetry.py` and keep a thin local wrapper for framework instrumentation.
- Non-Python repositories should keep the same OTLP contract and use a local implementation or a language-specific shared helper.

If a repository cannot export telemetry in a given runtime, it must still document the same OTLP contract and state the exact limitation instead of omitting observability guidance.

## Minimum Artifact Set

The minimum artifact set for a downstream product repository is:

### Governance and Operating Contract

- `AGENTS.md`
- `Repository.md`
- `phases-index.md`
- `guidelines-index.yaml`

### Product Definition

- `docs/requirements/mission.md`
- `docs/requirements/use-cases.md`
- `docs/requirements/user-flows.md`

### Technical and Quality Design

- `docs/architecture/system-design.md`
- `docs/qa/test-strategy.md`
- `docs/sre/deployment-and-operations.md`
- documented observability stack and OTLP contract

### Delivery and Verification

- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`
- `sonar-project.properties`
- `sonar.py`
- at least one test suite under `tests/`

## Role Boundaries

- `BA` and `PO` own product framing and behavioral intent.
- `SWE` owns architecture, implementation, and application-level support for the visible last-commit line.
- `QA` owns test strategy, release evidence, and merge-quality verification.
- `SRE` owns deployment readiness, runtime checks, rollback expectations, and observability requirements.

Cross-role boundary note:

- `SWE` is accountable for implementation and testability hooks.
- `QA` is accountable for verification content and gate interpretation.
- `SRE` is accountable for deployment safety and runtime confidence after release.

## Definition of Ready

A downstream product repository is ready for agentic delivery when:

- the repository has a stable home for requirements, architecture, QA, and SRE artifacts,
- the CI path is running and enforced,
- the deploy path is documented and executable,
- SonarQube integration is wired for supported codebases,
- the observability stack and OTLP contract are documented for the repository type,
- the visible last-commit line is implemented for user-facing products,
- the minimum artifact set exists and has clear ownership.
