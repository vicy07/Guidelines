# Phases Index and Role Matrix

Version: 1.3.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

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
| Solution Design | BA, SWE, SRE, QA | Architecture decisions, security/reliability controls, test strategy alignment, requirements impact alignment |
| Implementation | BA, SWE, QA, SRE | Implemented changes, traceability, readiness checks, requirement-change impact control |
| Verification | BA, QA, SWE, SRE | Test evidence, defect status, go/no-go recommendation, requirement acceptance traceability |
| Operations | BA, SRE, SWE, QA | Incident handling, RCA, post-fix validation, preventive actions, requirement-impact triage |

## Role-to-Guideline Links

- PO: `Requirements/README.md` (co-owner of requirements standards)
- BA: `Requirements/README.md` (primary owner of requirements standards; `PO` is co-owner)
- SWE: `SWE/README.md`
- QA: `QA/README.md`
- SRE: `SRE/README.md`
- Shared product behavior source: `Requirements/README.md`
- Downstream product repository template: `Product-Repository-Blueprint.md`

## Mandatory Rule

Each delivery must explicitly state:
- current phase,
- active roles,
- role-owned checks completed.
