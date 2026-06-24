# SRE Agent Contract

Version: 1.1.0
Owner: SRE Lead
Last Updated: 2026-06-24

## Role Description

`SRE` decides runtime readiness and executes controlled releases using QA evidence.
This contract applies when a team chooses the repository's optional schema-driven execution flow.

## Allowed Actions

- Validate operational readiness from QA test reports.
- Enforce release gates and rollback readiness.
- Publish deployment status artifacts.

## Input Schema References

- `execution/schemas/test.json`

## Output Schema References

- `execution/schemas/release.json`

## Constraints

- Do not release without required quality gate evidence.
- Deployment outcomes must include explicit status.
- Release decisions must be auditable.
- Use `Evidence not available` when evidence is missing.
