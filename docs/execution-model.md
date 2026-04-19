# Execution Model

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

## Execution Contracts

- Requirement contract: `execution/schemas/requirement.json`
- Task contract: `execution/schemas/task.json`
- Role contracts: `agents/*.md`
- Runtime flow: `runtime/orchestration.yaml`
- Runtime phases: `runtime/phases.yaml`

## Runtime Behavior

1. Validate input artifacts against schemas.
2. Execute role step using role-specific prompt and contract.
3. Validate output artifacts before transition.
4. Block transition on failed validation.
5. Persist outputs as auditable execution evidence.

## Handoff Rules

- `BA -> SWE`: requirement payload.
- `SWE -> QA`: code and task outputs.
- `QA -> SRE`: test report.
- `SRE -> completion`: deployment status.

## Error Handling

- Missing required fields: reject artifact.
- Invalid schema: block phase transition.
- Missing evidence: emit `Evidence not available` and escalate.
