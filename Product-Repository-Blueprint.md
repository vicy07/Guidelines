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
    architecture.md
    technical-architecture.md
    architecture/
      code-intelligence.md
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
  AGENTS.md
  audits.py
  audits/
    config/
      sonar-project.properties
      trivy.yaml
    scanners/
      sonar.py
      trivy.py
  code-intel.py
  code-intel/
    config/
      index.yaml
    index/
      manifest.json
      files.json
      symbols.json
      edges.json
      chunks.json
```

## Structure Rules

- `docs/requirements/` is the product behavior source of truth.
- `docs/architecture.md` is the repository-level architecture entry point and navigation hub and should follow the content contract from `Areas/requirements/architecture-standard.md`.
- `docs/technical-architecture.md` is the technical architecture source of truth for runtime boundaries, storage, integrations, and non-trivial technical decisions.
- `docs/architecture/` remains the home for optional ADRs and deeper architecture records when the repository needs them.
- `docs/architecture/code-intelligence.md` documents the project-specific implementation of the mandatory code-intelligence baseline defined by this repository and should follow the content contract from `Areas/requirements/code-intelligence-standard.md`.
- `docs/qa/` captures how the project proves quality.
- `docs/sre/` captures how the project is deployed, observed, rolled back, and operated.
- `src/` contains implementation code.
- `tests/` contains automated verification assets organized by test level.
- `audits/` contains repo-local orchestration and configuration for quality and security scanners.
- `code-intel/` contains repo-local code-intelligence configuration and generated index artifacts and must remain separate from `audits/`.
- `.github/workflows/` contains delivery automation that enforces minimum quality gates.

## Minimum Delivery Requirements

### 1. CI

Every project must define a CI workflow that:

- runs on pull requests and protected-branch pushes,
- installs dependencies deterministically,
- runs the fastest meaningful automated checks for the repository,
- runs at least a smoke regression set before merge,
- fails the build on test, security-gate, or quality-gate failure.

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

- `audits/config/sonar-project.properties`,
- repo-local Sonar wiring under `audits.py` and `audits/`,
- coverage report generation wired into the Sonar run,
- a required quality gate for `main` and release branches.

Recommended integration model:

1. Keep project-specific config in the product repo.
2. Reuse shared logic from this repository's `Tools/audits/` as the primary local orchestration layer.
3. Use `Tools/sonar/sonar_runner.py` as the lower-level Sonar runner behind that orchestration.
4. Do not add a root `sonar.py` entrypoint as part of the baseline model.
5. Fail the check if the SonarQube quality gate is not `OK`.

### 4. Trivy

Every repository must provide:

- `audits/config/trivy.yaml`,
- a filesystem scan in CI that covers dependency vulnerabilities, misconfigurations, and secrets,
- an image scan before deployment when the repository produces deployable container images,
- a documented suppression path for accepted findings, preferably via `.trivyignore` plus owner/ticket/expiry notes in repository documentation or comments.

Recommended integration model:

1. Keep project-specific targets, suppressions, severity thresholds, and report wiring in the product repo.
2. Reuse shared logic from this repository's `Tools/audits/` as the primary local orchestration layer.
3. Use `Tools/trivy/trivy_runner.py` as the lower-level Trivy runner behind that orchestration.
4. When the repository adopts `Tools/audits`, Trivy must run through Docker and must not require a host `trivy` installation on `PATH`.
5. Do not add a root `trivy.py` entrypoint as part of the baseline model.
6. Fail the gate on `HIGH` and `CRITICAL` findings, or on an explicitly documented equivalent threshold.

If image scanning does not apply to a repository, the repository must document why instead of omitting the Trivy gate entirely.

### 5. Visible Release Traceability

Every user-facing solution must render a persistent visible line:

`Last commit: <localized date/time> | <short sha>`

If commit details are unavailable, the UI must still render:

`Last commit: unavailable`

This requirement defines the visible product outcome, not the implementation mechanism.
The visible line must resolve correctly in deployed environments too, not only in local development.

### 6. Observability Stack

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

- Python repositories can copy or vendor `Tools/otel/telemetry.py` and keep a thin local wrapper for framework instrumentation.
- Non-Python repositories should keep the same OTLP contract and use a local implementation or a language-specific shared helper.

If a repository cannot export telemetry in a given runtime, it must still document the same OTLP contract and state the exact limitation instead of omitting observability guidance.

### 7. Code Intelligence Baseline

Every downstream repository must provide a mandatory code-intelligence baseline.

Required control surface:

- `code-intel.py`
- `code-intel/config/index.yaml`
- `code-intel/index/manifest.json`
- `code-intel/index/files.json`
- `code-intel/index/symbols.json`
- `code-intel/index/edges.json`
- `code-intel/index/chunks.json`
- `docs/architecture/code-intelligence.md`

Mandatory baseline rules:

- code understanding must be AST-first and must not rely on text search alone when indexed artifacts are available,
- the canonical baseline toolchain is `SCIP + ast-grep + rg`,
- `SCIP` is the preferred semantic source when the repository has configured indexers for its enabled languages,
- Tree-sitter may remain only as a fallback path until `SCIP` normalization reaches parity for the active language set,
- functions, classes, interfaces, methods, and modules must be indexed as first-class symbols,
- call, dependency, containment, and reference relationships must be materialized as graph edges,
- semantic retrieval must operate at symbol or chunk granularity rather than file-only granularity,
- reindexing must be incremental for touched files and directly affected graph relationships,
- context assembly for agentic retrieval must follow `AST -> Graph -> Semantic Search -> LLM`,
- generated `code-intel/index/` artifacts must not be committed to git,
- downstream repositories must ignore `code-intel/index/` and any raw tool-native artifact directories under that tree.

Recommended integration model:

1. Keep repository-specific scope, exclusions, language enablement, and embedding settings in the product repo.
2. Use `code-intel.py` as the repo-local control surface instead of overloading `audits.py`.
3. Reuse shared logic from this repository's `Tools/code-intel/` as the lower-level runtime behind that entrypoint.
4. Keep `SCIP` indexer commands repo-local because they are language-specific, but run the baseline through a reproducible container path when practical.
5. Do not require a host parser installation as the only supported execution path.
6. Treat `code-intel/` as an extensible repo-local capability area; adjacent generators such as C4 diagram builders may live there later, but the AST index is mandatory first.

## Minimum Artifact Set

The minimum artifact set for a downstream product repository is:

### Governance and Operating Contract

- `AGENTS.md`

Governance rule:

- `AGENTS.md` must link to the governing `Guidelines` repository or the adopted baseline documents used by the repository.
- preferred form: use public GitHub links for the repository reference point and for the primary baseline documents.

### Product Definition

- `docs/requirements/mission.md`
- `docs/requirements/use-cases.md`
- `docs/requirements/user-flows.md`

### Technical and Quality Design

- `docs/architecture.md`
- `docs/technical-architecture.md`
- `docs/architecture/code-intelligence.md`
- `docs/qa/test-strategy.md`
- `docs/sre/deployment-and-operations.md`
- documented observability stack and OTLP contract

### Delivery and Verification

- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`
- `audits.py`
- repo-local `audits/`
- `code-intel.py`
- repo-local `code-intel/`
- `audits/config/sonar-project.properties`
- `audits/config/trivy.yaml`
- at least one test suite under `tests/`

## Compliance Audit Artifact

When a downstream product repository undergoes a compliance audit against this baseline, the repository must create `docs/audits/` if it does not already exist.

Each compliance audit must save its findings inside `docs/audits/` and include:

- the audit date,
- the audited repository scope,
- the findings and missing artifacts discovered,
- the evidence reviewed,
- the exact `Guidelines` version used for the audit, pinned by commit hash and commit date.

This requirement applies only after a compliance audit is run. It is not a mandatory baseline artifact for repositories that have not yet been audited.

## Role Boundaries

- `BA` and `PO` own product framing and behavioral intent.
- `SWE` owns architecture, implementation, and application-level support for the visible last-commit line.
- `SWE` also owns the code-intelligence architecture contract, repo-local `code-intel.py` implementation, and symbol/index schema choices inside the baseline.
- `QA` owns test strategy, release evidence, merge-quality verification, and verification that required code-intelligence artifacts are produced as documented.
- `SRE` owns deployment readiness, runtime checks, rollback expectations, observability requirements, release-time security scanning gates, and reproducible execution of the code-intelligence runtime in CI or containerized workflows.

Cross-role boundary note:

- `SWE` is accountable for implementation and testability hooks.
- `QA` is accountable for verification content, gate interpretation, and artifact-level validation of the code-intelligence baseline.
- `SRE` is accountable for deployment safety, runtime confidence after release, and operational handling of code-intelligence caches or generated artifacts.

## Definition of Ready

A downstream product repository is ready for agentic delivery when:

- the repository has a stable home for requirements, architecture, QA, and SRE artifacts,
- the CI path is running and enforced,
- the deploy path is documented and executable,
- SonarQube integration is wired for supported codebases through the repo-local audit entrypoint,
- Trivy integration is wired for repository filesystem scanning and deployable-image scanning where applicable through the repo-local audit entrypoint,
- the observability stack and OTLP contract are documented for the repository type,
- the code-intelligence baseline is wired through `code-intel.py`, documented in `docs/architecture/code-intelligence.md`, and produces the required JSON artifacts,
- the visible last-commit line is implemented for user-facing products,
- the minimum artifact set exists and has clear ownership.
