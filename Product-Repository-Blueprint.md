# Product Repository Blueprint (Agentic Development Baseline)

## Purpose

Define the minimum recommended baseline for downstream software product repositories that want predictable agentic delivery without forcing a specific stack.

## Design Rules

- Keep the baseline small enough to adopt in real projects.
- Preserve the product repository's chosen language, framework, and deployment platform.
- Standardize only the parts that improve agent and human coordination.
- Prefer incremental adoption over big-bang repository rewrites.

## Applicability

Select `docs-only`, `library-cli`, `service-web`, or `critical-system` and a
`basic`/`indexed` code-intelligence mode using
[`Repository Applicability Profiles`](Areas/requirements/repository-profiles.md).
Record the selection, accountable owner and rationale in
`.governance/baseline.yaml`. Mixed repositories must cover their highest-risk
components; existing stricter local contracts require explicit migration.

The structure below shows a product repository with optional indexed tooling.
Product documentation remains the minimum set; `docs-only` repositories use
README-based scope/ownership/verification instead of empty product artifacts.
`code-intel.py`, `code-intel/`, and their generated outputs apply only to
`indexed` mode. Runtime deployment/telemetry paths apply to shipped runtimes;
security and lifecycle controls still cover documentation build tools.

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
      eol.yaml
      sonar-project.properties
      trivy.yaml
    scanners/
      eol.py
      sonar.py
      trivy.py
    sbom/
      components.cdx.json
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

- The root `AGENTS.md` references both the
  [`Guidelines`](https://github.com/vicy07/Guidelines) engineering baseline and
  the [`AI-Governance`](https://github.com/vicy07/AI-Governance) agent operating
  model, then records any explicit product-specific exceptions.
- `docs/requirements/` is the product behavior source of truth.
- `docs/architecture.md` is the repository-level architecture entry point and navigation hub and should follow the content contract from `Areas/requirements/architecture-standard.md`.
- `docs/technical-architecture.md` is the technical architecture source of truth for runtime boundaries, storage, integrations, and non-trivial technical decisions.
- `docs/architecture/` remains the home for optional ADRs and deeper architecture records when the repository needs them.
- `docs/architecture/code-intelligence.md` documents the selected basic/indexed code-intelligence mode defined by this repository and should follow the content contract from `Areas/requirements/code-intelligence-standard.md`.
- `docs/qa/` captures how the project proves quality.
- `docs/sre/` captures how the project is deployed, observed, rolled back, and operated.
- `src/` contains implementation code.
- `tests/` contains automated verification assets organized by test level.
- `audits/` contains repo-local orchestration and configuration for quality, security, and component-lifecycle scanners plus the tracked enriched SBOM.
- `code-intel/` contains repo-local code-intelligence configuration and generated index artifacts and must remain separate from `audits/`.
- `.github/workflows/` contains delivery automation that enforces minimum quality gates.

## Minimum Delivery Requirements

### 1. CI

Every project must define a CI workflow that:

- runs on pull requests and protected-branch pushes,
- installs dependencies deterministically,
- runs the fastest meaningful automated checks for the repository,
- runs at least a smoke regression set before merge,
- fails the build on failures of checks selected by the documented CI policy.

Execution frequency is governed by
[`CI Verification Policy`](guidelines/playbooks/ci-verification-policy.md).
Ordinary PR/push CI must not run full audits, SonarQube, full Trivy scans,
network EOL refresh, or full index rebuilds unconditionally. Run fast checks
for the change; select targeted risk checks, approved schedules, and release
checks separately. Required release gates may consume fresh candidate evidence.

Minimum CI outcome:

- the repository can prove that a change was built and checked before merge,
- the result is visible in pull requests and branch history.

### 2. CD and Deployment

Every deployable project must define a deployment path that includes:

- a documented target environment model,
- a Git-based workflow that publishes committed repository state,
- post-deploy verification,
- rollback or roll-forward guidance,
- ownership of deployment approval and runtime checks.

Production application code must never be deployed, redeployed, uploaded, or otherwise published directly through a hosting-platform CLI, UI, or API. Platform tools may be used read-only for diagnostics and post-deploy verification, but code publication must always flow from Git through the documented delivery workflow.

If a repository is a library and is not deployed as a runtime service, replace deployment guidance with a documented release/publish flow.

### 3. SonarQube

Every supported codebase must provide:

- `audits/config/sonar-project.properties`,
- repo-local Sonar wiring under `audits.py` and `audits/`,
- coverage report generation wired into the Sonar run,
- a required quality gate for supported `main`/release candidates, evaluated
  through scheduled or explicitly triggered analysis and fresh release evidence
  under the CI Verification Policy; no unconditional Sonar run on each CI event.

Recommended integration model:

1. Keep project-specific config in the product repo.
2. Reuse shared logic from this repository's `Tools/audits/` as the primary local orchestration layer.
3. Use `Tools/sonar/sonar_runner.py` as the lower-level Sonar runner behind that orchestration.
4. Do not add a root `sonar.py` entrypoint as part of the baseline model.
5. Fail the check if the SonarQube quality gate is not `OK`.

### 4. Trivy

Every repository must provide:

- `audits/config/trivy.yaml`,
- filesystem scanning for dependency vulnerabilities, misconfigurations, and
  secrets on an approved schedule, applicable change trigger, and release
  readiness when fresh candidate evidence is unavailable; no full scan on
  every PR/push by default,
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

### 5. Component Lifecycle and EOL Audit

Every repository must continuously inventory and assess:

- direct and transitive libraries, frameworks, runtimes, base images, operating systems, and build tools,
- third-party APIs, SaaS products, managed services, platforms, identity/payment/data providers, and similar external dependencies,
- first-party architectural components including applications, services, workers, data stores, queues, gateways, and scheduled jobs.

Required downstream contract:

- `audits/config/eol.yaml`,
- `audits/scanners/eol.py`,
- tracked CycloneDX JSON at `audits/sbom/components.cdx.json`,
- `python audits.py eol scan` for evidence refresh and assessment,
- `python audits.py eol check` for deterministic validation of committed state,
- EOL check inclusion in `python audits.py all`, CI, scheduled monitoring, and release readiness.

The enriched SBOM must include stable component identity and relationships plus owner, component class, criticality, lifecycle status/EOL, evidence source and freshness, risk, rationale, and remediation details. `unknown` lifecycle evidence must remain explicit and must not be interpreted as supported.

Criticality and risk classification, failure thresholds, exception controls, and the minimum weekly monitoring cadence are normative in `Areas/swe/component-lifecycle-guidelines.md`. Vulnerability scanning does not replace lifecycle monitoring.

### 6. Visible Release Traceability

Every user-facing solution must render a persistent visible line:

`Last commit: <localized date/time> | <short sha>`

If commit details are unavailable, the UI must still render:

`Last commit: unavailable`

This requirement defines the visible product outcome, not the implementation mechanism.
The visible line must resolve correctly in deployed environments too, not only in local development.

### 7. Observability Stack

Observability follows the selected repository profile. Document the actual
diagnostic path, owners, critical signals and limitations; do not install an
exporter or collector solely to satisfy the blueprint.

- `docs-only`: build, validation and publication diagnostics; no runtime telemetry.
- `library-cli`: actionable diagnostics, CLI exit codes/verbosity and host-owned
  logging/instrumentation hooks; no automatic telemetry/exporter setup.
- `service-web`: service logs, health/error and user-impact metrics; tracing
  where needed across component boundaries; applicable frontend diagnostics
  and correlation with data minimization.
- `critical-system`: correlated logs/metrics/traces for critical paths, owned
  alerts and measurable reliability/recovery objectives. Missing signals need
  reviewed compensating controls and verification.

The product repository owns runtime wiring. OpenTelemetry is a reusable option;
when OTLP export is used, document service attribution, protocol and endpoint:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

Python projects using OTLP can copy/vendor `Tools/otel/telemetry.py`; other
stacks use appropriate local instrumentation. Libraries leave exporter setup
to their host. Static content does not require client tracking. Existing
operational controls must not be removed without an explicit impact review.

### 8. Code Intelligence Baseline

All product repositories document navigation mode and adequacy in
`docs/architecture/code-intelligence.md`, following
`Areas/requirements/code-intelligence-standard.md`.

- `basic`: repository map, text search and existing editor/language navigation.
  No custom entrypoint, AST index, graph, embeddings or container is required.
- `indexed`: justified by repeated navigation/change-impact needs; follow the
  indexed contract in `docs/architecture/code-intelligence.md` in this baseline.
  `code-intel.py` and `code-intel/config/index.yaml` provide the separate local
  control surface. Generated artifacts are `manifest.json`, `files.json`,
  `symbols.json`, `edges.json`, and `chunks.json` under `code-intel/index/`.

`SCIP + ast-grep + rg` is the shared runner's reference implementation, not a
universal requirement. Select supported tools from actual language coverage.
Semantic/vector retrieval is optional and must be backed by a real provider
and retrieval evidence; a null embedding does not provide semantic search.
Fresh indexes can aid analysis; simple searches do not require an AST-first
pipeline. Rebuild incrementally when useful under the CI Verification Policy.

Generated `code-intel/index/` artifacts must not be committed to git;
downstream repositories must ignore `code-intel/index/` and its raw artifacts.
Reuse `Tools/code-intel/` when useful and keep indexed commands separate from
`audits.py`. Do not invent unimplemented capabilities or commands.

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
- documented profile-appropriate diagnostics and OTLP contract when export is used

### Delivery and Verification

The code-intelligence entrypoint/config/tree below is required only in
`indexed` mode. Deployment applies to deployable runtimes; libraries/CLI use
release/publishing guidance. Docs-only scope follows the profile contract.

- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`
- `audits.py`
- repo-local `audits/`
- `audits/config/eol.yaml`
- `code-intel.py`
- repo-local `code-intel/`
- `audits/config/sonar-project.properties`
- `audits/config/trivy.yaml`
- `audits/scanners/eol.py`
- `audits/sbom/components.cdx.json`
- at least one test suite under `tests/`

## Compliance Audit Artifact

When a downstream product repository undergoes a compliance audit against this baseline, the repository must create `docs/audits/` if it does not already exist.

One audit work item or coordinated audit run must produce exactly one
consolidated human-readable report named
`docs/audits/YYYY-MM-DD-<scope>.md`, for example
`docs/audits/2026-07-23-guidelines-compliance.md`. Do not split the same audit
across per-tool, per-role, remediation, or re-gate Markdown reports. Machine
artifacts such as JSON, SARIF, logs, and SBOMs may remain separate and must be
linked from the consolidated report.

Each report must include:

- the audit date,
- the audited repository scope,
- the findings and missing artifacts discovered,
- the evidence reviewed,
- the exact `Guidelines` version used for the audit, pinned by commit hash and commit date.
- explicit coverage of Guidelines compliance, EOL/component lifecycle, Trivy
  filesystem and image scanning, security, and GDPR/privacy;
- the method (`tool/runner`, `AI review`, `manual review`, or `mixed`) and status
  (`passed`, `failed`, `blocked`, `not-run`, or `not-applicable`) for every area;
- the reason, gate impact, and follow-up for every check that was not run or was
  not applicable;
- a final `go`, `no-go`, `conditional`, or `blocked` decision.

The complete content and evidence contract is normative in
`guidelines/playbooks/audit-reporting-standard.md`. Audit execution is opt-in:
normal delivery and QA must not start the full audit suite without an explicit
audit request or approved schedule. AI-based GDPR/privacy review is a gap
assessment and must not be presented as legal certification.

This requirement applies only after a compliance audit is run. It is not a mandatory baseline artifact for repositories that have not yet been audited.

## Role Boundaries

- `BA` and `PO` own product framing and behavioral intent.
- `SWE` owns architecture, implementation, and application-level support for the visible last-commit line.
- `SWE` owns code-navigation mode/adequacy, and in indexed mode the repo-local
  `code-intel.py` implementation and symbol/index schema choices.
- `SWE` owns SBOM inventory completeness, architecture/dependency relationships, criticality classification, and lifecycle-risk remediation design.
- `QA` owns test strategy, release evidence, merge-quality verification, lifecycle-gate behavior, and verification that required SBOM and code-intelligence artifacts are produced as documented.
- `SRE` owns deployment readiness, runtime checks, rollback expectations, observability requirements, scheduled EOL monitoring and alerting, release-time security/lifecycle gates, and reproducible execution of the code-intelligence runtime in CI or containerized workflows.

Cross-role boundary note:

- `SWE` is accountable for implementation and testability hooks.
- `QA` is accountable for verification content, gate interpretation, and artifact-level validation of the SBOM and code-intelligence baselines.
- `SRE` is accountable for deployment safety, runtime confidence after release, authoritative lifecycle evidence refresh, and operational handling of generated artifacts.

## Definition of Ready

A downstream product repository is ready for agentic delivery when:

- the repository has a stable home for requirements, architecture, QA, and SRE artifacts,
- the CI path is running and enforced,
- the deploy path is documented and executable,
- SonarQube integration is wired for supported codebases through the repo-local audit entrypoint,
- Trivy integration is wired for repository filesystem scanning and deployable-image scanning where applicable through the repo-local audit entrypoint,
- lifecycle/EOL monitoring is wired through the repo-local audit entrypoint, covers libraries, third parties, runtimes/build tools, and architectural components, and persists current criticality and risk in the tracked SBOM,
- the selected profile has documented diagnostic coverage and, when used, OTLP export,
- navigation mode and adequacy are documented; indexed mode has its entrypoint,
  configuration, generated artifacts and coverage/freshness verification,
- the visible last-commit line is implemented for user-facing products,
- the minimum artifact set exists and has clear ownership.
