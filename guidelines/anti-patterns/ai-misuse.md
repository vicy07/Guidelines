# AI Misuse Anti-Patterns

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

## Purpose

Capture common failure modes when operating agent-driven delivery systems and shared guideline repositories.

## Anti-Patterns

### Overusing Agents

- Splitting trivial tasks into too many agent calls.
- Creating parallel work without ownership boundaries.
- Delegating decisions that require accountable human approval.

### No Validation

- Accepting generated outputs without deterministic checks.
- Skipping validation before guidance is reused or propagated.
- Treating narrative status updates as release evidence.

### No Contract Discipline

- Allowing prompts, templates, or examples to drift from the guidance they are supposed to support.
- Keeping duplicate instructions that disagree about the same workflow.
- Evolving repository contracts without explicit versioning or migration notes.

## Prevention Controls

- Enforce explicit review and validation gates for shared standards.
- Keep one clear source of truth per workflow or contract.
- Block propagation of unclear or unverified guidance into downstream repositories.
