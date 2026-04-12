# Implementation Guidelines

Version: 1.0.0
Owner: SWE Lead
Last Updated: 2026-04-12

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
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Module ownership is explicit.
- Requirement-to-code traceability is documented.
- Security and reliability impacts are reviewed.
- QA handover includes test scope and risk notes.
- SRE handover includes deployment and observability implications.