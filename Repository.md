# Guidelines Repository Structure Standard

## Purpose

Define the canonical structure of this guidelines repository so agents and humans can quickly find phase, role, and dependency instructions.

## Scope Boundary

- This document describes the physical structure and navigation model of this repository.
- Downstream product repository recommendations are defined in `Product-Repository-Blueprint.md`.

## Required Root Structure

```text
<guidelines-repo>/
  Requirements/
  SWE/
  QA/
  SRE/
  scripts/
  .github/
  README.md
  Repository.md
  Product-Repository-Blueprint.md
  AGENTS.md
  phases-index.md
  guidelines-index.yaml
```

## Top-Level Ownership

- `Requirements/` - shared product-behavior standards (primary owner: `BA`, co-owner: `PO`) used by all role guidelines.
- `SWE/` - software engineering standards and technical decision guidance.
- `QA/` - verification and quality standards.
- `SRE/` - reliability, operations, and incident standards.
- `scripts/` - repository validation/maintenance scripts.

## Instruction Retrieval Path

1. Start with `phases-index.md` to identify current lifecycle phase and active roles.
2. Use `guidelines-index.yaml` to resolve role-owned files and dependencies.
3. Open role README and normative files in `SWE/`, `QA/`, `SRE/`.
4. Use `Requirements/` files as behavior source of truth (owned by `BA`, with `PO` co-ownership).
5. Follow `AGENTS.md` for execution contract and instruction priority.

## Governance Files

- `AGENTS.md` - execution contract and precedence rules for agents.
- `phases-index.md` - phase-to-role matrix.
- `guidelines-index.yaml` - machine-readable ownership/dependency index.
- `Repository.md` - structure/navigation standard for this repository.
- `Product-Repository-Blueprint.md` - baseline template for downstream product repositories.

## Conflict Resolution Order

If instructions conflict, apply this precedence:
1. User request in the current task
2. `AGENTS.md`
3. `guidelines-index.yaml`
4. `phases-index.md`
5. Role/domain guideline file being edited (`Requirements` / `SWE` / `QA` / `SRE`)
6. `Requirements` standards
7. `Repository.md`
8. `Product-Repository-Blueprint.md` (for downstream repository structure recommendations)

## Definition of Ready (Guidelines Repository)

This repository is ready when:
- Root structure matches this file.
- `phases-index.md` and `guidelines-index.yaml` are aligned with real file paths.
- Role folders contain active guidelines with clear ownership.
- Normative files include required metadata fields (`Version`, `Owner`, `Last Updated`).
- Validation pipeline passes (for example, `npm run validate-guidelines` when configured).
