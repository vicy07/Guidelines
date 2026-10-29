# UI/UX Standard

Version: 1.3.0
Owner: UX
Last Updated: 2026-08-06

## Metadata (required)

- Version
- Owner
- Last Updated
- Platform Scope (web/mobile/pwa)

## Ownership Boundary

- Primary standard owner role: `UX`
- Governance roles: `BA` (primary requirements owner) and `PO` (requirements co-owner)
- Consumer roles: `SWE`, `QA`, `SRE`
- `UX` owns interaction, information architecture, visual style, content style, and accessibility guidance.
- `UX` owns the repository UX artifacts and evidence trail for research, flows, usability validation, design decisions, and UX outcomes.
- `BA` and `PO` own product intent, scope, business rules, and acceptance direction across `requirements-standards`.
- If a UI/UX change alters product behavior, terminology, or acceptance criteria, the related requirements standards must be updated as well.

## Required Sections

1. Design Principles
2. Information Architecture
3. Interaction Rules
4. Visual Style
5. Content Style
6. Accessibility
7. Responsive Behavior
8. Component Consistency
9. UX Metrics
10. Research, Hypotheses, and Validation
11. UX Artifact and Evidence Contract

## Design Rules

- `Low friction`: critical daily tasks are completed in the minimum number of steps.
- `Operational clarity`: booking, payment, and attendance states are readable without interpretation.
- `Error prevention`: the interface prevents overbooking and critical input errors.
- Start from the user's goal and context; do not design screens before the relevant user flow and problem are understood.
- Reuse existing product patterns and design-system components before introducing new interaction patterns.

## Visual Style Rules

- Define tokens for color, spacing, typography, radius, and shadows.
- Contrast and hierarchy are mandatory for statuses (`booked`, `waitlist`, `paid`, `unpaid`).
- System statuses must use consistent patterns across all screens.

## Content Rules

- Button labels must be actions (`Book Session`, `Confirm Payment`).
- Error messages must explain the reason and the next step.
- Session-change messages must always include date, time, and required user action.
- User-facing AI behavior must distinguish generated content, uncertainty, sources, pending work, failure, and user confirmation when applicable.
- User-facing flows must not use dark patterns to obtain consent, payment, data, retention, or continued engagement.
- Every user-facing solution must render a persistent status/footer line on every primary screen in the format `Last commit: <localized date/time> | <short sha>`.
- If commit details are not available, keep the same visible line and render `Last commit: unavailable`.

## Accessibility Rules

- Minimum text contrast: WCAG AA.
- Full keyboard navigation is required for key scenarios.
- Semantic markup and visible focus states are mandatory.
- Touch targets, zoom/reflow, screen-reader names, status announcements, and reduced-motion behavior must be considered for applicable platforms.

## UX Research and Validation Rules

- Use the lifecycle `Research -> Insights -> Hypotheses -> Prototype -> Usability Test -> Findings -> Design Decision -> Result` when research or experimentation is required.
- Every material UX hypothesis must state the user/problem, expected behavior, evidence source, baseline or known gap, success signal, test method, owner, and decision date.
- Findings must distinguish observed evidence, interpretation, and unresolved uncertainty. Do not invent user research, personas, metrics, or usability results.
- UX decisions that change product behavior, terminology, scope, or acceptance must update the related requirements and user-flow artifacts with BA/PO.

## UX Artifact and Evidence Contract

- Prefer the downstream repository's existing canonical UX documentation location.
- When no documented location exists and UX work is material, use `docs/ux/` with durable records for guidelines, research, user flows, design decisions, usability tests, and metrics.
- Keep source design decisions and test findings reviewable in the repository; external Figma or prototype links are references, not the only source of truth.
- For each material UX change, record affected flow, states, accessibility implications, implementation handoff, verification method, evidence status, and follow-up owner.
- Generated exports or screenshots may supplement UX artifacts but must not replace the textual contract, flow logic, acceptance states, or decision record.

## Quality Checklist

- There is a specification for each key screen from user flows.
- Every form has defined validation states.
- Every list has empty, loading, and error states.
- Mobile-first adaptation is verified on major breakpoints.
- Material UX decisions have a repository artifact and an evidence status.
- UX hypotheses have a validation method, success signal, owner, and decision date.
- Commit status visibility is verified on login, dashboard, and detail flows for each user-facing solution.
- Commit status content is verified in the deployed environment, not only in local or preview development.

## Template

```md
# UI/UX Guidelines - <Product>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Platform Scope: <web/mobile/pwa>

## 1. Design Principles
...

## 2. Information Architecture
...

## 3. Interaction Rules
...

## 4. Visual Style
...

## 5. Content Style
...

## 6. Accessibility
...

## 7. Responsive Behavior
...

## 8. Component Consistency
...

## 9. UX Metrics
...

## 10. Research, Hypotheses, and Validation
...

## 11. UX Artifact and Evidence Contract
...
```
