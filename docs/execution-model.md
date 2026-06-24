# Structured Execution Assets

Version: 1.2.0
Owner: Repository Maintainer
Last Updated: 2026-06-24

## Purpose

Describe the optional structured-execution assets stored in this repository.
These assets support teams that want schema-validated role handoffs, but they are not the minimum adoption path for using this repository.

## Available Contracts

- Requirement contract: `execution/schemas/requirement.json`
- Task contract: `execution/schemas/task.json`
- Test contract: `execution/schemas/test.json`
- Release contract: `execution/schemas/release.json`
- Traceability contract: `execution/schemas/traceability.json`
- Role contracts: `agents/*.md`
- Runtime flow: `runtime/orchestration.yaml`
- Runtime phases: `runtime/phases.yaml`

## What These Assets Are For

Use the structured execution assets when a team needs:

- deterministic agent-to-agent handoffs,
- machine-readable artifacts,
- schema validation before phase transitions,
- auditable delivery evidence across roles.

## What They Are Not For

Do not treat these assets as mandatory just to adopt the repository baseline.
Teams can adopt the blueprint, minimum artifacts, CI/CD rules, deploy guidance, SonarQube integration, and visible last-commit requirement without running a schema-driven workflow.

## Runtime Behavior

When the structured execution layer is used:

1. validate input artifacts against schemas,
2. execute the role step using the matching contract,
3. validate output artifacts before transition,
4. block transition on failed validation,
5. preserve outputs as execution evidence.

## Canonical References

- End-to-end flow: `runtime/orchestration.yaml`
- Example chain: `execution/examples/chain-login-v1/`
- Shared requirement for missing evidence: `Evidence not available`
