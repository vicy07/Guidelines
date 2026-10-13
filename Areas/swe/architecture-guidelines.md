# Architecture Guidelines and Format Standard

Version: 1.4.0
Owner: Repository Maintainer
Last Updated: 2026-10-13

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Mission Version
- Related Use Cases Version

## Required Sections

1. Architecture Scope and Assumptions
2. System Context
3. Containers and Module Boundaries
4. Data Architecture
5. Integrations and Contracts
6. Non-Functional Requirements (NFR)
7. Security and Privacy
8. Reliability and Observability
9. Deployment and Environments
10. Risks, Trade-offs, and Constraints
11. Traceability (architecture -> use cases/business rules)

## Architecture Rules

- Architecture documents current decisions and explicitly marks planned changes.
- Module boundaries are defined by responsibilities and public contracts.
- Critical scenarios must state latency, availability, and consistency expectations.
- Every external interaction must specify protocol, owner, and error policy.
- Every major architecture agreement must include rationale and constraints.
- Architecture records the selected profile from
  `Areas/requirements/repository-profiles.md`, actual diagnostic signals and
  operational limitations; OTLP configuration applies when export is used.
- Product architecture references `docs/architecture/code-intelligence.md`
  for basic/indexed mode, rationale and navigation adequacy. Indexed mode
  records real symbol/graph coverage, freshness and incremental behavior;
  semantic retrieval is required only if selected and implemented.
- Every repository architecture must inventory first-party components, runtimes, and third-party services in the downstream SBOM and classify their criticality and lifecycle risk according to `Areas/swe/component-lifecycle-guidelines.md`.

## Diagram Rules

- Use the C4 approach for context and container views with consistent component naming.
- Diagrams must be synchronized with section text and must not contradict it.
- Data and flows must be explicit: source, direction, data type.
- If information is missing, state `Evidence not available` without assumptions.

## Writing Rules

- One section = one architecture level (context, containers, components, data).
- Decisions must be testable: what was chosen, why, and consequences.
- NFRs must be measurable (`p95 latency`, `RPO`, `RTO`, `uptime`, load limits).
- The Security and Privacy section references `Areas/swe/security-guidelines.md` as the source of controls.
- Reliability and Observability describes profile-required diagnostics, alert
  ownership and limitations. Declare OpenTelemetry/OTLP only when used;
  libraries leave exporters to the host. Critical signals need verified coverage.
- Constraints and risks are mandatory, including temporary decisions.

## Quality Checklist

- Every key use case is covered at container/module level.
- Data ownership, core entities, and consistency rules are documented.
- Integration policies include retry/timeout/idempotency.
- Logging, metrics, tracing, and alerting are defined for critical paths.
- Diagnostic coverage and any selected OpenTelemetry/OTLP configuration are documented.
- Basic navigation adequacy is documented; indexed mode additionally records
  entrypoint, JSON artifacts and actual retrieval capabilities/limitations.
- Architectural components and their dependency relationships are traceable to `audits/sbom/components.cdx.json`, with owner, criticality, lifecycle evidence, and risk.
- Security controls are specified: authN/authZ, secrets, audit trail.
- Security controls are aligned with `Areas/swe/security-guidelines.md`.
- Technical debt items and closure criteria are explicit.

## Template

```md
# Architecture Guidelines - <Product>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Mission Version: <x.y>
Related Use Cases Version: <x.y>

## 1. Architecture Scope and Assumptions
...

## 2. System Context
...

## 3. Containers and Module Boundaries
...

## 4. Data Architecture
...

## 5. Integrations and Contracts
...

## 6. Non-Functional Requirements (NFR)
...

## 7. Security and Privacy
...

## 8. Reliability and Observability
...

## 9. Deployment and Environments
...

## 10. Risks, Trade-offs, and Constraints
...

## 11. Traceability
...
```
