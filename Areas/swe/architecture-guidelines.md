# Architecture Guidelines and Format Standard

Version: 1.5.0
Owner: Repository Maintainer
Last Updated: 2026-08-06

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
- Every repository architecture must inventory first-party components, runtimes, and third-party services in the downstream SBOM and classify their licenses, license risk, criticality, and lifecycle risk according to `Areas/swe/component-lifecycle-guidelines.md`.
- Before approving a component or architecture option, the architecture must evaluate license compatibility against the intended build, linking, modification, hosting, commercial-use, packaging, and distribution model. Material obligations, restrictions, required notices/source offers, alternatives considered, and the accountable approval owner must be recorded under risks, trade-offs, and constraints.

## Repository Artifact Contract

- `docs/architecture.md` is the short, navigational entry point and must remain aligned with `Areas/requirements/architecture-standard.md`.
- `docs/technical-architecture.md` is the deep technical source of truth for runtime boundaries, storage, integrations, NFRs, security, observability, deployment, risks, and traceability.
- Material architecture decisions must be recorded as ADRs under `docs/architecture/adr/` unless the downstream repository has an equivalent documented decision-record location.
- C4, deployment, and data-model diagrams must be stored as source files under `docs/architecture/diagrams/` or the repository's documented equivalent. Rendered images are supplements, not the source of truth.
- Architecture reviews, assessments, and migration plans must be durable repository artifacts under `docs/architecture/` or an explicitly documented equivalent.
- Architecture work is incomplete when the code change and its required architecture artifacts are not updated in the same delivery change, or when the artifact owner, evidence, decision status, and follow-up are missing.
- The SWE/Architect role creates and maintains these technical artifacts; BA/PO own product intent and requirements, QA owns verification evidence, and SRE owns operational readiness and runtime evidence.

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
- Architectural components and their dependency relationships are traceable to `audits/sbom/components.cdx.json`, with owner, license expression/type/evidence, license obligations and risk, criticality, lifecycle evidence, and lifecycle risk.
- Component choices with material license obligations or restrictions have an explicit compatibility decision before implementation; missing evidence is not treated as approval.
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
