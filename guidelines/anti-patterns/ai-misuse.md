# AI Misuse Anti-Patterns

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

## Purpose

Capture common failure modes when operating agent-driven delivery systems.

## Anti-Patterns

### Overusing Agents

- Splitting trivial tasks into too many agent calls.
- Creating parallel work without ownership boundaries.
- Delegating decisions that require accountable human approval.

### No Validation

- Accepting generated outputs without deterministic checks.
- Skipping artifact validation before phase transition.
- Treating narrative status updates as release evidence.

### No Schema Enforcement

- Exchanging untyped payloads between roles.
- Allowing prompt outputs to drift from expected format.
- Evolving contracts without versioned schema changes.

## Prevention Controls

- Enforce schema validation in runtime gates.
- Require role-specific output contracts per phase.
- Block orchestration progress on invalid payloads.
