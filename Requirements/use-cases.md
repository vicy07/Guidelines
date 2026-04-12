# Use Cases Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Mission Version

## Required Sections

1. Actors
2. Preconditions
3. Trainer Use Cases
4. Client Use Cases
5. Business Rules
6. Edge Cases
7. Traceability (use case -> business rule)

## Use Case Card Format

Each use case must follow a unified format:
- ID
- Goal
- Trigger
- Main Flow
- Alternative Flow
- Exceptions
- Postconditions
- Related Rules

## Writing Rules

- One use case describes one user goal.
- Main Flow contains only the happy path.
- Alternatives and errors are documented separately.
- Rules must not be duplicated across multiple use cases.

## Quality Checklist

- All roles from mission are covered by use cases.
- Every use case is linked to at least one business rule.
- Boundary states are specified (capacity, waitlist, cancellation, payment).

## Template

```md
### UC-<ROLE><N>: <Name>

Goal: ...
Trigger: ...
Preconditions: ...

Main Flow:
1. ...
2. ...

Alternative Flow:
1. ...

Exceptions:
- ...

Postconditions:
- ...

Related Rules:
- BR-...
```