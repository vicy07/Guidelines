# AGENTS Operating Contract

## Purpose

Define deterministic behavior for AI agents using this repository as a reusable guidelines baseline for agentic development.
This repository stores reusable guidelines; downstream product-repository structure guidance is documented in `Product-Repository-Blueprint.md`, with rollout guidance in `Adoption-Guide.md`.
Requirements standards are owned primarily by `BA` with `PO` co-ownership.

## Instruction Priority

Apply instructions in this order:
1. User request in the current task
2. `AGENTS.md`
3. `guidelines-index.yaml`
4. `phases-index.md`
5. Role/domain guideline file being edited (`Requirements` / `SWE` / `QA` / `SRE`)
6. `Requirements` standards
7. `Repository.md`
8. `Product-Repository-Blueprint.md` (for downstream repository structure recommendations)
9. `Adoption-Guide.md` (for rollout guidance into new or existing repositories)

If two rules conflict, follow the higher-priority rule and report the conflict.

## Required Workflow

1. Start with `README.md` unless the task is already scoped to a specific guideline file.
2. Identify current phase from `phases-index.md` when the task changes repository guidance or role-owned standards.
3. Identify active roles for this phase.
4. Load role-owned guideline files and direct dependencies from `guidelines-index.yaml` only for the areas touched by the task.
5. If the task asks for downstream product repository recommendations, load `Product-Repository-Blueprint.md` and `Adoption-Guide.md`.
6. Apply minimal, focused changes.
7. Validate:
   - metadata for normative files,
   - dependency/reference integrity,
   - role ownership consistency.
8. Report:
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
