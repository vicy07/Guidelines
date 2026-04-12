# Phases Index and Role Matrix

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Purpose

Provide a single-file phase map showing which roles are primary in each lifecycle phase.

## Phases

1. Discovery
2. Solution Design
3. Implementation
4. Verification
5. Operations

## Role Matrix

| Phase | Primary Roles | Required Role Outputs |
|---|---|---|
| Discovery | PO, BA, SWE, QA, SRE | Scope, use cases, constraints, acceptance criteria |
| Solution Design | SWE, SRE, QA | Architecture decisions, security/reliability controls, test strategy alignment |
| Implementation | SWE, QA, SRE | Implemented changes, traceability, readiness checks |
| Verification | QA, SWE, SRE | Test evidence, defect status, go/no-go recommendation |
| Operations | SRE, SWE, QA | Incident handling, RCA, post-fix validation, preventive actions |

## Role-to-Guideline Links

- SWE: `SWE/README.md`
- QA: `QA/README.md`
- SRE: `SRE/README.md`
- Shared product behavior source: `Requirements/README.md`

## Mandatory Rule

Each delivery must explicitly state:
- current phase,
- active roles,
- role-owned checks completed.