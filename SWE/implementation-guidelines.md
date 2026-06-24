# Implementation Guidelines

Version: 1.1.0
Owner: SWE Lead
Last Updated: 2026-06-24

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

- Every change must map to an explicit module owner.
- Behavior changes must be traceable to requirements/use cases.
- Architectural boundaries must not be bypassed for convenience.
- Temporary fixes must include debt records and closure criteria.
- If a service emits telemetry, implementation handover must include the exact OTLP protocol and endpoint values expected in each runtime environment.
- For user-facing projects, implementation must preserve the project's chosen technology and architecture while delivering the required visible status/footer line: `Last commit: <localized date/time> | <short sha>`.
- If commit details are not available, keep the same visible line and render `Last commit: unavailable`.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Module ownership is explicit.
- Requirement-to-code traceability is documented.
- Security and reliability impacts are reviewed.
- QA handover includes test scope and risk notes.
- SRE handover includes deployment and observability implications.
