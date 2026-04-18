# AGENTS Operating Contract

## Purpose

Define deterministic behavior for AI agents using this repository as a role-driven solution playbook.
This repository stores reusable guidelines; downstream product-repository structure guidance is documented in `Product-Repository-Blueprint.md`.

## Instruction Priority

Apply instructions in this order:
1. User request in the current task
2. `AGENTS.md`
3. `guidelines-index.yaml`
4. `phases-index.md`
5. Role guideline file being edited (`SWE` / `QA` / `SRE`)
6. `Requirements` standards
7. `Repository.md`

If two rules conflict, follow the higher-priority rule and report the conflict.

## Required Workflow

1. Identify current phase from `phases-index.md`.
2. Identify active roles for this phase.
3. Load role-owned guideline files and direct dependencies from `guidelines-index.yaml`.
4. If the task asks for downstream product repository recommendations, load `Product-Repository-Blueprint.md` as supporting guidance.
5. Apply minimal, focused changes.
6. Validate:
   - metadata for normative files,
   - dependency/reference integrity,
   - role ownership consistency.
7. Report:
   - changed files,
   - assumptions,
   - unresolved risks.

## Role and Ownership Rules

- Every change must map to at least one role owner.
- Cross-role changes must keep explicit boundary notes (what each role is accountable for).
- If ownership is ambiguous, pause and escalate before broad edits.

## Editing Rules

- Do not invent facts. Use `Evidence not available` when evidence is missing.
- Preserve stable naming unless migration is requested.
- Do not remove required sections silently.
- Prefer incremental changes over broad rewrites.

## Output Contract

Each completion must include:
- changed file list,
- validation summary,
- unresolved risks and required follow-up actions.
