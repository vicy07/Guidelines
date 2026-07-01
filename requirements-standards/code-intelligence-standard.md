# Code Intelligence Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-07-01

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related Implementation Guidelines Version

## Purpose

Define the required content contract for a downstream product repository's `docs/architecture/code-intelligence.md`.

This standard defines what the downstream document must cover.
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

- The document must describe the repository's actual `code-intel.py` entrypoint and must not describe hypothetical commands that are not implemented.
- The configuration section must point to the real repo-local config path, normally `code-intel/config/index.yaml`.
- The artifact section must name the required JSON artifacts: `manifest.json`, `files.json`, `symbols.json`, `edges.json`, and `chunks.json`.
- The Git policy section must explicitly state that generated `code-intel/index/` artifacts are not committed to git.
- The toolchain section must state which path is active for the repository now: `SCIP`, fallback Tree-sitter, or another documented baseline-compatible combination.
- The scope section must list the indexed languages and the repository areas included or excluded from indexing.
- The limitations section must use `Evidence not available` when semantic coverage, freshness, or parity is not proven.

## Quality Checklist

- The downstream document clearly separates local implementation details from the shared baseline.
- Command examples match the repo-local CLI surface.
- Artifact paths and ignore policy match the real repository layout.
- Indexed languages and directories are explicit.
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
