# Execution Model

Version: 1.1.0
Owner: Repository Maintainer
Last Updated: 2026-04-24

## Execution Contracts

- Requirement contract: `execution/schemas/requirement.json`
- Task contract: `execution/schemas/task.json`
- Test contract: `execution/schemas/test.json`
- Release contract: `execution/schemas/release.json`
- Traceability contract: `execution/schemas/traceability.json`
- Role contracts: `agents/*.md`
- Runtime flow: `runtime/orchestration.yaml`
- Runtime phases: `runtime/phases.yaml`
- Canonical chain example: `execution/examples/chain-login-v1/`

## Runtime Behavior

1. Validate input artifacts against schemas.
2. Execute role step using role-specific prompt and contract.
3. Validate output artifacts before transition.
4. Block transition on failed validation.
5. Persist outputs as auditable execution evidence.

## Handoff Rules

- `BA -> SWE`: requirement payload.
- `SWE -> QA`: task bundle linked to requirement id.
- `QA -> SRE`: test report linked to task ids.
- `SRE -> completion`: release payload linked to test report id.

## Error Handling

- Missing required fields: reject artifact.
- Invalid schema: block phase transition.
- Missing evidence: emit `Evidence not available` and escalate.
