# Requirements Standards

This section defines unified standards for product requirements documentation.

## Ownership

- Primary owner role: `BA`
- Co-owner role: `PO`
- Consumer roles: `SWE`, `QA`, `SRE`

## Scope

- `architecture-standard.md` - required content contract for downstream `docs/architecture.md`
- `mission-standard.md` - mission and product framing standard
- `use-cases-standard.md` - role-based functional scenario standard
- `user-flows-standard.md` - step-by-step user journey standard
- `ui-ux-guidelines-standard.md` - interface, content, and visual style standard
- `code-intelligence-standard.md` - required content contract for downstream `docs/architecture/code-intelligence.md`

## Global Rules

- One document = one goal and one artifact type.
- Every document must include `Version`, `Owner`, and `Last Updated`.
- The `Owner` field should normally be `BA` (or an explicitly delegated owner approved by `BA`/`PO`).
- Statements must be testable and unambiguous.
- Business terms must remain consistent across documents.
- Any change affecting product behavior must update at least one of the relevant requirement standards.

## Naming

- Files are stored in lower-kebab-case.
- Use stable identifiers inside documents:
  - Use case: `UC-T1`, `UC-C2`
  - User flow: `UF-BOOK-01`
  - UI rule: `UI-01`
