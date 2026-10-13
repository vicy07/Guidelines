# Repository Applicability Profiles

Version: 1.0.0
Owner: BA
Last Updated: 2026-10-13

## Purpose and Ownership

Select engineering controls by shipped behavior, runtime, and consequence of
failure. BA/PO own scope and business criticality; SWE owns navigation/tooling
choices; SRE owns runtime diagnostics and operational risk; QA owns evidence
that the selected controls work. Profiles describe applicability, not maturity
levels, security exemptions, or the number of agents to run.

## Profile Matrix

| Profile | Applicable scope | Documentation | Observability |
|---|---|---|---|
| `docs-only` | Documentation or standards without a shipped application/library/CLI; documentation build/validation tooling may exist | README records purpose, structure, ownership, verification/publishing and limitations; no empty product-document scaffold | Build/CI/publishing diagnostics; no runtime collector, metrics, traces or client tracking required |
| `library-cli` | Reusable library or finite command-line tool | Product minimum document set; release/publish guidance replaces service deployment | Actionable errors and diagnostics; CLI exit status and optional verbosity; library logging/instrumentation hooks controlled by host; no automatic exporter, collector or background telemetry |
| `service-web` | Hosted service, worker, web application or deployed frontend | Product minimum document set and applicable runtime/deployment design | Service logs, health/error and user-impact metrics; tracing where needed to explain cross-component failures; frontend error diagnostics/correlation where applicable; no mandatory tracking of static content |
| `critical-system` | Failure can materially affect security/privacy boundaries, money, critical availability, data integrity or recovery, regardless of packaging | Product minimum document set plus measurable critical-path, recovery and security acceptance criteria | Correlated logs, metrics and traces for critical paths, owned alerts and measurable service/recovery objectives; missing signals need an owned, reviewed compensating control and verification |

All profiles require the dual-baseline `AGENTS.md`, a pinned adoption record,
applicable fast CI, ownership, and honest evidence. Security, dependency/EOL,
release and rollback controls still apply to actual tooling and shipped
artifacts. A docs-only repository with a vulnerable documentation builder
cannot exempt that dependency from security/lifecycle checks.

A mixed repository must cover every shipped component and use the highest
applicable risk profile; critical code is not downgraded because most files
are Markdown. Record per-component distinctions in the technical design.
A finite CLI is not a service; a long-running daemon follows service controls.
Client telemetry must minimize sensitive data and follow product privacy
requirements; the profile is not permission to collect data.

## Code Intelligence Modes

Every product repository keeps `docs/architecture/code-intelligence.md` as a
short record of its chosen mode, commands, scope, limitations and rationale.
Docs-only repositories can keep basic navigation guidance in the README.

- `basic`: repository map, text search and existing editor/language navigation
  are sufficient. No custom `code-intel.py`, SCIP index, graph, embeddings or
  container is required. Verify representative code-location/change-impact
  tasks; record limitations rather than claiming semantic coverage.
- `indexed`: choose when repeated cross-module navigation or impact analysis
  justifies the setup and maintenance cost. Implement the stable control
  surface/artifacts from `docs/architecture/code-intelligence.md`, document
  language coverage and freshness, and verify representative retrieval tasks.
  Embeddings and vector search are optional capabilities, not implied by an
  index or a JSON field. Criticality alone does not prove an index is useful.

SWE and QA record why the selected mode is adequate. Critical systems need
explicit evidence that navigation and change-impact review cover their
critical paths even when using `basic`. A change in size, language, architecture
or defect pattern triggers reassessment; no arbitrary file-count threshold
automatically forces an index.

## OpenTelemetry and OTLP

OpenTelemetry is a reusable implementation option. An OTLP protocol/endpoint
contract is required when OTLP export is actually used; otherwise document the
chosen diagnostic path and relevant limitations. Do not add nonfunctional OTLP
variables or a collector solely to satisfy a template. Libraries must let the
host opt into instrumentation and own exporter setup. Critical-system signal
requirements remain applicable independently of the selected telemetry vendor.

## Adoption Record and Migration

New adoptions select the profile and code-intelligence mode in
`.governance/baseline.yaml`, using the existing revision-lock template:

```yaml
adoption:
  profile: service-web
  code_intelligence: basic
  owner: product-engineering
  rationale: Single service with language navigation; cross-component tracing is not currently needed.
```

The owner must identify an accountable team/role and the rationale must explain
scope, risk and capability choices. Keep detailed evidence in existing product
architecture/QA/SRE documents instead of duplicating it in the lock file.

- Existing pinned baselines and stricter product instructions remain effective
  until an explicit adoption/migration change records the new revision,
  profile, rationale, affected controls, verification and residual risks.
- Do not delete working indexes or telemetry solely because a lighter profile
  exists. Removing an operational control requires impact review and evidence
  that required outcomes remain covered.
- Without an adoption block, the structural checker preserves its previous
  eight-document requirement and does not infer exemptions. Invalid or partial
  adoption records are gaps, never a fallback to a lighter profile.
- The checker verifies references, revision pins, declaration shape and static
  artifact presence. It does not prove profile classification, telemetry,
  security, retrieval accuracy or runtime compliance; those require QA/SRE
  evidence. Generated indexes remain runtime artifacts, outside this check.

## Verification and Review

- BA/PO confirm runtime scope and critical business/security consequences.
- SWE confirms mode, supported languages, actual commands and coverage limits.
- SRE confirms diagnostics, alert ownership, retention and applicable export.
- QA verifies representative navigation/impact tasks and observable failure
  diagnostics, plus critical alerts/recovery behavior where applicable.
- Record `Evidence not available` for unproven coverage. Reassess selection when
  scope/risk changes; do not mark missing capabilities as passing.
