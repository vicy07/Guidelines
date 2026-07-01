# Architecture Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-07-01

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Mission Version
- Related Use Cases Version

## Purpose

Define the required content contract for a downstream product repository's `docs/architecture.md`.

This standard defines what the downstream architecture entry document must cover.
Detailed technical design rules remain governed by `SWE/architecture-guidelines.md` and normally apply to `docs/technical-architecture.md`.

## Required Sections

1. Purpose and Scope
2. System Summary
3. Repository Architecture Map
4. Runtime or Container Overview
5. Key Boundaries and Responsibilities
6. Cross-References to Detailed Design
7. Constraints and Evidence Gaps

## Section Rules

- The document must stay short and navigational and must not become the only place where deep technical design lives.
- The repository architecture map must point to the real downstream artifacts, including `docs/technical-architecture.md`, `docs/requirements/`, `docs/qa/`, and `docs/sre/`.
- The runtime or container overview must describe the major runtime shape at a high level and defer deep protocol, storage, and NFR details to `docs/technical-architecture.md`.
- The boundaries section must identify the main system areas or modules and who or what owns them conceptually.
- The cross-reference section must explicitly link to the deeper documents that carry technical detail, including `docs/architecture/code-intelligence.md` when the baseline requires it.
- The constraints section must use `Evidence not available` where repository architecture details are not yet proven.

## Quality Checklist

- The downstream document is understandable as the first architecture entry point.
- It clearly separates navigation and high-level architecture from deep technical design.
- Linked downstream artifacts match the real repository layout.
- Key boundaries and responsibilities are explicit.
- Missing or immature details are marked without invented certainty.

## Template

```md
# Architecture

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Mission Version: <x.y>
Related Use Cases Version: <x.y>

## 1. Purpose and Scope
...

## 2. System Summary
...

## 3. Repository Architecture Map
...

## 4. Runtime or Container Overview
...

## 5. Key Boundaries and Responsibilities
...

## 6. Cross-References to Detailed Design
...

## 7. Constraints and Evidence Gaps
...
```
