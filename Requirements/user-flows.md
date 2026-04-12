# User Flows Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Use Cases Version

## Required Sections

1. Flow Index
2. Flow Definitions
3. States and Transitions
4. Decision Points
5. Failure Paths
6. Notifications/Side Effects

## Flow Definition Format

Each flow must follow a unified format:
- Flow ID (`UF-...`)
- Actor
- Goal
- Entry Conditions
- Steps
- Decision Nodes
- Exit States
- Error States
- Telemetry Events

## Writing Rules

- Each step must be atomic and observable.
- Every decision node must have at least 2 outcomes.
- Error states must include a recovery path.
- Step names must follow verb + object (`Select session`, `Confirm booking`).

## Quality Checklist

- Every critical use case has at least one user flow.
- All side effects (notifications, charges, status changes) are explicitly documented.
- There is a dedicated flow for cancellation and one for payment failure.

## Template

```md
### UF-<DOMAIN>-<NN>: <Name>

Actor: ...
Goal: ...
Entry Conditions: ...

Steps:
1. ...
2. ...

Decision Nodes:
- D1: if ... -> ... / ...

Exit States:
- ...

Error States:
- ...

Telemetry Events:
- ...
```