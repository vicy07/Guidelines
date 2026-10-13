# Code Intelligence Standard

Version: 2.0.0
Owner: Repository Maintainer
Last Updated: 2026-10-13

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related Implementation Guidelines Version

## Purpose

Define the required content contract for a downstream product repository's `docs/architecture/code-intelligence.md`.

This standard defines what the downstream document must cover. Select `basic`
or `indexed` using `Areas/requirements/repository-profiles.md`. Product
repositories keep a short document in either mode; docs-only basic navigation
can live in README. Retain the sections below, marking indexed-only sections
not applicable with the selection rationale rather than inventing commands.
The technical baseline itself remains defined by `docs/architecture/code-intelligence.md` in this repository.

## Required Sections

1. Purpose and Scope
2. Local Control Surface
3. Configuration Location
4. Artifact Layout
5. Git and Retention Policy
6. Active Toolchain and Fallback Policy
7. Indexed Repository Scope
8. Incremental Update Behavior
9. Known Limitations and Evidence Gaps

## Section Rules

- Describe actual search/navigation commands in basic mode; indexed mode
  describes the real `code-intel.py` entrypoint. Do not invent commands.
- Indexed configuration points to the real repo-local config path, normally
  `code-intel/config/index.yaml`; basic mode has no mandatory custom config.
- In indexed mode, the artifact section must name the required JSON artifacts: `manifest.json`, `files.json`, `symbols.json`, `edges.json`, and `chunks.json`.
- In indexed mode, Git policy explicitly excludes generated `code-intel/index/`
  artifacts from commits; basic mode marks generated artifacts not applicable.
- State the active navigation/indexing tools, language coverage and limitations.
  The shared `SCIP + ast-grep + rg` runner is a reference implementation.
  Semantic retrieval needs an actual provider and evidence; null embeddings
  and substring lookup must not be described as vector search.
- Scope lists navigable languages/areas and, for indexed mode, included and
  excluded index paths. Record representative navigation/change-impact checks.
- The limitations section must use `Evidence not available` when semantic coverage, freshness, or parity is not proven.

## Quality Checklist

- The downstream document clearly separates local implementation details from the shared baseline.
- Command examples match the repo-local CLI surface.
- Artifact paths and ignore policy match the real repository layout.
- Navigable languages/areas and any selected indexed directories are explicit.
- Fallback behavior and limitations are documented without inventing unsupported coverage.

## Template

```md
# Code Intelligence

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Architecture Version: <x.y>
Related Implementation Guidelines Version: <x.y>

## 1. Purpose and Scope
...

## 2. Local Control Surface
...

## 3. Configuration Location
...

## 4. Artifact Layout
...

## 5. Git and Retention Policy
...

## 6. Active Toolchain and Fallback Policy
...

## 7. Indexed Repository Scope
...

## 8. Incremental Update Behavior
...

## 9. Known Limitations and Evidence Gaps
...
```
