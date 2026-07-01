# Code Intelligence Baseline

Version: 1.1.0
Owner: Repository Maintainer
Last Updated: 2026-07-01

## Purpose

Define the mandatory code-intelligence baseline that this `Guidelines` repository imposes on downstream product repositories.
This document is the normative design contract for the baseline itself.
Each downstream project must implement that contract in its own `docs/architecture/code-intelligence.md`.
The required section structure for that downstream document is governed separately by `requirements-standards/code-intelligence-standard.md`.

## Ownership Split

- `Guidelines` owns the standard: required structure, mandatory toolchain contract, required artifacts, and behavioral rules.
- Each downstream product repository owns the implementation: configured languages, excluded paths, runtime wiring, update cadence, and documented limitations.
- Downstream repositories must document missing capabilities as `Evidence not available` instead of inventing support.

## Required Downstream Structure

Every downstream product repository must provide:

```text
<project-repo>/
  code-intel.py
  code-intel/
    config/
      index.yaml
    index/
      manifest.json
      files.json
      symbols.json
      edges.json
      chunks.json
  docs/
    architecture/
      code-intelligence.md
```

`code-intel.py` is a dedicated repo-local entrypoint.
It must not be merged into `audits.py` because code intelligence is a separate control surface from security and quality scanners.

## Mandatory Toolchain Baseline

- `SCIP + ast-grep + rg` is the mandatory baseline toolchain contract.
- `SCIP` is the preferred semantic source for symbols and graph edges when the active language has a configured indexer.
- `ast-grep` is the mandatory structural matching layer.
- `rg` is the mandatory text fallback and validation layer.
- Repositories should run the shared runtime through Docker or an equivalently reproducible container path.
- A downstream repository must not depend on a manually installed host parser binary as the only supported execution path.
- Tree-sitter is allowed only as a fallback runtime while `SCIP` coverage is unavailable or not yet at feature parity for the repository's enabled languages.

## Mandatory Behavioral Rules

Every downstream implementation must support these rules:

- AST-first code understanding: repository analysis starts from syntax trees and symbol relationships, not text search alone.
- Symbol-level indexing: functions, classes, interfaces, methods, and modules are indexed as first-class entities.
- Graph-based navigation: call, dependency, containment, and reference relationships are materialized explicitly.
- Embedding granularity: semantic retrieval operates at symbol or chunk level, not only file level.
- Incremental indexing: after changes, the repository reindexes only touched files and graph-adjacent artifacts that need refresh.
- Retrieval pipeline: context preparation follows `AST -> Graph -> Semantic Search -> LLM`.

## Required Artifact Contract

The downstream JSON artifacts must provide at least:

- `manifest.json` - schema version, tool version, commit identity, engine identity, generation timestamp, and artifact inventory.
- `files.json` - indexed files, language classification, fingerprints, and index status.
- `symbols.json` - symbol identities, kinds, source ranges, parent relationships, and module ownership.
- `edges.json` - call, import, reference, containment, and dependency edges between indexed symbols.
- `chunks.json` - symbol-level or chunk-level retrieval units, including embedding payloads or embedding references.

The runtime may additionally persist raw tool-native artifacts, for example:

- `code-intel/index/scip/index.scip`
- `code-intel/index/ast-grep/`

These raw artifacts are optional supplements. They do not replace the mandatory normalized JSON contract.

The artifact schema can evolve, but these logical responsibilities must remain stable unless the baseline is intentionally migrated.
The generated JSON artifacts are required runtime outputs, but they must not be committed to git by downstream repositories.
Downstream repositories should ignore `code-intel/index/` and any raw tool-native artifact directories beneath that tree.

## Repo-Local Runtime Contract

The preferred downstream commands are:

- `python code-intel.py index`
- `python code-intel.py graph`
- `python code-intel.py embeddings`
- `python code-intel.py query <symbol-or-pattern>`
- `python code-intel.py config`

The exact CLI implementation stays repo-local, but downstream repositories must document the implemented command set in their own `docs/architecture/code-intelligence.md`.

The preferred repo-local configuration must also declare:

- enabled languages,
- include and exclude paths,
- `SCIP` indexer commands per language when available,
- whether Tree-sitter fallback remains enabled for parity coverage.

## Agent Working Rules

When code-intelligence artifacts are present and fresh enough for the current revision:

- agents should prefer symbol, graph, and chunk retrieval over text-only search,
- agents should use text search mainly for bootstrapping, validation, or locating non-code assets,
- agents must document stale or missing index coverage as `Evidence not available` when the index cannot support a requested analysis.

Downstream rollout discipline:

- apply the baseline through the smallest repo-local surface that works first,
- keep the first rollout focused on `code-intel.py`, repo-local config, ignore rules, and `docs/architecture/code-intelligence.md`,
- Do not add extra downstream docs, tests, or planning artifacts unless the repository explicitly asks for them or existing repository contracts require them.

## Relationship to Future Capabilities

`code-intel/` is intentionally extensible.
The mandatory AST index is the first required capability.
Adjacent repository-local capabilities, such as generated C4 diagrams or other code-navigation assets, may live under the same control surface as long as they do not weaken the mandatory indexing baseline.

## Transition Note

The baseline has moved from a Tree-sitter-primary model to a `SCIP + ast-grep + rg` model.
During migration, downstream repositories may keep Tree-sitter fallback enabled until their language set has a working `SCIP` path and the normalized JSON artifacts remain complete.

## Role Boundaries

- `SWE` owns architecture and implementation of the code-intelligence baseline.
- `QA` owns verification that the entrypoint, JSON artifacts, and incremental-update behavior work as documented.
- `SRE` owns reproducible execution in CI or containerized release paths and the operational handling of caches or generated artifacts.
