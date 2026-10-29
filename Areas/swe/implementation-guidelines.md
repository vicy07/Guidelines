# Implementation Guidelines

Version: 1.8.0
Owner: SWE Lead
Last Updated: 2026-10-29

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related QA Strategy Version

## Required Sections

1. Implementation Scope
2. Module Ownership
3. Coding Standards
4. Dependency Management
5. Change Traceability
6. Technical Debt Handling
7. Handover to QA/SRE

## Rules

- Follow `guidelines/playbooks/delivery-policy.md` for coherent changes, review,
  merge readiness, releasable `main` and revision traceability.

- Every change must map to an explicit module owner.
- Behavior changes must be traceable to requirements/use cases.
- Architectural boundaries must not be bypassed for convenience.
- Temporary fixes must include debt records and closure criteria.
- Implement the selected profile from `Areas/requirements/repository-profiles.md`;
  document diagnostics and any actual OTLP export contract.
- Every repository must implement a repository-local Trivy entrypoint for filesystem scanning, and repositories that produce deployable container images must also define an image-scanning entrypoint before release.
- Every repository must implement repo-local component audit entrypoints and maintain the enriched tracked CycloneDX SBOM required by `Areas/swe/component-lifecycle-guidelines.md`, including license expression/value, license type, evidence, material obligations or restrictions, and license risk for each in-scope component.
- Basic navigation uses existing search/editor/language tools and a short
  adequacy record. Indexed mode implements separate `code-intel.py` and
  `code-intel/` configuration/artifacts under the indexed design contract;
  the shared SCIP/ast-grep/rg runtime is optional.
- Use fresh symbol/graph retrieval where it helps; text search remains valid
  for focused lookups and unindexed content. Do not claim missing coverage.
- Service/web diagnostics follow the profile's runtime signals; critical paths
  retain correlated logs/metrics/traces and owned alerts or reviewed controls.
- Libraries provide host-controlled diagnostic/instrumentation hooks; CLI
  tools provide actionable errors, exit status and optional verbosity. Do not
  install exporters, background telemetry or collectors automatically.
- Docs-only repositories need build/CI/publication diagnostics, not runtime
  telemetry. Static content does not require client tracking.
- Implementation handover must include the exact Trivy invocation path, config file location, and the ownership record for any accepted suppressions.
- Implementation handover must include the component scan/check paths, SBOM location, license and lifecycle evidence sources, monitoring cadence, component owners, material license obligations/restrictions, and open remediation plans.
- Handover records basic navigation commands/adequacy or, for indexed mode,
  entrypoint/config/artifacts, language coverage, freshness and limitations.
- When OTLP export is used, handover includes actual protocol/endpoint values
  for each applicable runtime environment, for example:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

- For user-facing projects, implementation must preserve the project's chosen technology and architecture while delivering the required visible status/footer line: `Last commit: <localized date/time> | <short sha>`.
- The deployed implementation must source that visible line from metadata that exists in the target runtime; do not assume a local `.git` checkout is available in production containers or hosted runtimes.
- If commit details are not available, keep the same visible line and render `Last commit: unavailable`.
- Every published release must have a reviewed versioned note under `docs/releases/X.Y.Z.md` or the repository's documented equivalent. Release automation may draft or render these notes, but the committed note and any tracked release-notes page input must exist before the CI artifact is built and promoted.
- For a user-facing solution with a web page, implement a release-notes page backed by that versioned source and expose it through primary navigation or the required persistent footer/status line. Treat the page and link as a user-facing delivery surface, including accessibility and deployed-environment verification.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Module ownership is explicit.
- Requirement-to-code traceability is documented.
- Security and reliability impacts are reviewed.
- Security scanning entrypoints and suppression ownership are documented.
- Component inventory, criticality, EOL evidence, risk, and remediation ownership are documented in the downstream SBOM.
- Navigation mode/adequacy and any selected index entrypoints, artifacts and update boundaries are documented.
- Profile-required diagnostics and any selected OTLP export implications are documented.
- QA handover includes test scope and risk notes.
- SRE handover includes deployment and observability implications.
- Release handover identifies the versioned notes, source commit, release-notes page when applicable, and the verified public navigation or footer link.
