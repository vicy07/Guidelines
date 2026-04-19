# SWE Agent Contract

Version: 1.0.0
Owner: SWE Lead
Last Updated: 2026-04-19

## Role Description

`SWE` converts validated requirements into implementable, testable engineering tasks and delivery-ready changes.

## Allowed Actions

- Analyze validated requirement payloads.
- Decompose feature work into implementation tasks.
- Define technical dependencies and sequencing.
- Produce handoff-ready outputs for `QA` and `SRE`.

## Input Schema References

- `execution/schemas/requirement.schema.json`

## Output Schema References

- `execution/schemas/task.schema.json`

## Constraints

- Do not change requirement intent.
- Do not emit unstructured output.
- Task IDs must be stable and unique per feature.
- Output must be valid JSON and schema-compatible.
- Use `Evidence not available` when evidence is missing.
