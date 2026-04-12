# Repository Structure Standard

## Purpose

Define the canonical structure for this repository so all contributors store and maintain artifacts consistently.

## Required Root Structure

```text
<repo-root>/
  Requirements/
  SWE/
  QA/
  SRE/
  Artifacts/
  scripts/
  .github/
  README.md
  Repository.md
  AGENTS.md
  phases-index.md
  guidelines-index.yaml
```

## Top-Level Ownership

- `Requirements/` - product behavior standards (shared source of truth)
- `SWE/` - software engineering guidelines and architecture/security ownership
- `QA/` - verification and quality ownership
- `SRE/` - operations, reliability, and incident ownership
- `Artifacts/` - produced artifacts, outputs, and evidence from delivery cycles

## Artifact Placement Rules

- Discovery/design documents go to `Artifacts/<initiative>/discovery` and `Artifacts/<initiative>/design`.
- Verification reports and evidence go to `Artifacts/<initiative>/verification`.
- Incident and post-fix artifacts go to `Artifacts/<initiative>/operations`.
- Do not store transient files outside `Artifacts/` unless explicitly required by tooling.

## Governance Rules

- `AGENTS.md` defines execution behavior for AI agents.
- `phases-index.md` defines lifecycle phase-to-role mapping in one file.
- `guidelines-index.yaml` is the machine-readable dependency map.
- If a conflict exists, resolve in this order:
  1. User request
  2. `AGENTS.md`
  3. `guidelines-index.yaml`
  4. Role guideline file
  5. `Repository.md`

## Definition of Ready (Repository)

A repository is ready when:
- Root structure matches this file.
- Role folders contain active guidelines with ownership.
- `phases-index.md` exists and maps phases to roles.
- `guidelines-index.yaml` is aligned with real file paths.
- CI passes `npm run validate-guidelines`.