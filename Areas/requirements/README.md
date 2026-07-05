# Requirements Standards

This section defines unified standards for product requirements documentation.

## Ownership

- Primary owner role: `BA`
- Co-owner role: `PO`
- Adjacent specialist area: `Areas/ux/` owns UI/UX standards consumed by `SWE`, `QA`, and `SRE`
- Consumer roles: `SWE`, `QA`, `SRE`

## Scope

- `architecture-standard.md` - required content contract for downstream `docs/architecture.md`
- `mission-standard.md` - mission and product framing standard
- `use-cases-standard.md` - role-based functional scenario standard
- `user-flows-standard.md` - step-by-step user journey standard
- `code-intelligence-standard.md` - required content contract for downstream `docs/architecture/code-intelligence.md`
- Adjacent area reference: `../ux/ui-ux-guidelines-standard.md` - interface, content, and visual style standard

## Global Rules

- One document = one goal and one artifact type.
- Every document must include `Version`, `Owner`, and `Last Updated`.
- The `Owner` field should normally be `BA` (or an explicitly delegated owner approved by `BA`/`PO`).
- Statements must be testable and unambiguous.
- Business terms must remain consistent across documents.
- Any change affecting product behavior must update at least one of the relevant requirement standards.
- UI/UX guidance lives in `Areas/ux/`, but changes that affect behavior, terminology, or acceptance direction must still update the relevant requirements standards.

## Naming

- Files are stored in lower-kebab-case.
- Use stable identifiers inside documents:
  - Use case: `UC-T1`, `UC-C2`
  - User flow: `UF-BOOK-01`
  - UI rule: `UI-01`
