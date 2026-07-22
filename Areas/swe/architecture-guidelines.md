# Architecture Guidelines and Format Standard

Version: 1.3.0
Owner: Repository Maintainer
Last Updated: 2026-07-22

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
- Every repository architecture must define its observability stack and explain how logs, metrics, and traces are produced for its repository type.
- Every repository architecture must define or explicitly reference `docs/architecture/code-intelligence.md` as the source of truth for the mandatory code-intelligence baseline, including the `SCIP + ast-grep + rg` toolchain, symbol boundaries, graph relationships, incremental reindex behavior, and retrieval pipeline.
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
- The Reliability and Observability section must declare the OpenTelemetry attribution and OTLP export contract or explicitly document why a runtime cannot emit telemetry directly.
- Constraints and risks are mandatory, including temporary decisions.

## Quality Checklist

- Every key use case is covered at container/module level.
- Data ownership, core entities, and consistency rules are documented.
- Integration policies include retry/timeout/idempotency.
- Logging, metrics, tracing, and alerting are defined for critical paths.
- OpenTelemetry service attribution and OTLP export expectations are documented.
- The code-intelligence baseline documents the repo-local `code-intel.py` entrypoint, JSON artifact locations, and the `AST -> Graph -> Semantic Search -> LLM` retrieval flow.
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
