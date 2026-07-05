# Phases Index and Role Matrix

Version: 1.4.0
Owner: Repository Maintainer
Last Updated: 2026-07-05

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

- PO: `Agents/PO.md` (role profile; governing standards remain in `Areas/requirements/`)
- BA: `Agents/BA.md` (role profile; governing standards remain in `Areas/requirements/`)
- UX: `Agents/UX.md` (role profile; governing standards remain in `Areas/ux/`)
- SWE: `Agents/SWE.md` (role profile; governing standards remain in `Areas/swe/`)
- QA: `Agents/QA.md` (role profile; governing standards remain in `Areas/qa/`)
- SRE: `Agents/SRE.md` (role profile; governing standards remain in `Areas/sre/`)
- Shared product behavior source: `Areas/requirements/README.md`
- Downstream product repository template: `Product-Repository-Blueprint.md`

## Mandatory Rule

Each delivery must explicitly state:
- current phase,
- active roles,
- role-owned checks completed.
