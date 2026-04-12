# UI/UX Guidelines and Style Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Platform Scope (web/mobile/pwa)

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

## Design Rules

- `Low friction`: critical daily tasks are completed in the minimum number of steps.
- `Operational clarity`: booking, payment, and attendance states are readable without interpretation.
- `Error prevention`: the interface prevents overbooking and critical input errors.

## Visual Style Rules

- Define tokens for color, spacing, typography, radius, and shadows.
- Contrast and hierarchy are mandatory for statuses (`booked`, `waitlist`, `paid`, `unpaid`).
- System statuses must use consistent patterns across all screens.

## Content Rules

- Button labels must be actions (`Book Session`, `Confirm Payment`).
- Error messages must explain the reason and the next step.
- Session-change messages must always include date, time, and required user action.

## Accessibility Rules

- Minimum text contrast: WCAG AA.
- Full keyboard navigation is required for key scenarios.
- Semantic markup and visible focus states are mandatory.

## Quality Checklist

- There is a specification for each key screen from user flows.
- Every form has defined validation states.
- Every list has empty, loading, and error states.
- Mobile-first adaptation is verified on major breakpoints.

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
```