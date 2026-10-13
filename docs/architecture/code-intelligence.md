# Code Intelligence Baseline

Version: 2.0.0
Owner: Repository Maintainer
Last Updated: 2026-10-13

## Purpose

Define the basic navigation and optional indexed code-intelligence contract.
Applicability is governed by `Areas/requirements/repository-profiles.md`.
Basic mode requires no custom AST/SCIP stack, graph, embeddings or container.
Product repositories document mode/adequacy; docs-only basic navigation may
remain in README. The indexed sections below apply only when that mode is
explicitly selected.
This document is the normative design contract for the baseline itself.
Each product repository records the applicable contract in its own
`docs/architecture/code-intelligence.md`; basic mode marks indexed-only sections
not applicable with rationale.
The required section structure for that downstream document is governed separately by `Areas/requirements/code-intelligence-standard.md`.

## Ownership Split

- `Guidelines` owns the standard: required indexed structure, reference toolchain, required artifacts, and behavioral rules.
- Each downstream product repository owns the implementation: configured languages, excluded paths, runtime wiring, update cadence, and documented limitations.
- Downstream repositories must document missing capabilities as `Evidence not available` instead of inventing support.

## Required Downstream Structure

Every downstream repository selecting indexed mode must provide:

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

## Toolchain Selection

- `SCIP + ast-grep + rg` is the shared runner's reference toolchain. It is not
  mandatory for basic mode or for an indexed implementation with equivalent
  documented artifact/coverage behavior.
- For the shared runner, `SCIP` is the preferred symbol/reference source when
  the active language has a configured indexer. Semantic symbol resolution
  is distinct from optional vector-based retrieval.
- The shared runner uses `ast-grep` for structural matching when configured.
- Text search remains useful for bootstrapping, focused lookups and validation;
  basic mode can use existing search/editor/language tools.
- Repositories should run the shared runtime through Docker or an equivalently reproducible container path.
- A downstream repository must not depend on a manually installed host parser binary as the only supported execution path.
- Tree-sitter or other language tooling may provide an appropriate indexing
  path. Record actual symbol/relationship coverage, ambiguity and missing
  language support instead of promising feature parity.

## Behavioral Rules

Basic mode documents representative navigation/change-impact tasks and
limitations; no generated artifacts or fixed retrieval pipeline are required.
Indexed mode supports the following within its documented language scope:

- Use syntax/symbol relationships where they improve code understanding;
  do not force indexed retrieval for every lookup or for unindexed content.
- Symbol-level indexing: functions, classes, interfaces, methods, and modules are indexed as first-class entities.
- Graph-based navigation records supported call/dependency/containment/reference
  relationships explicitly and names unsupported or heuristic coverage.
- When semantic retrieval is selected, use actual symbol/chunk vectors or
  references to a working provider; verify retrieval on representative tasks.
  Null embedding fields and substring matching are not semantic retrieval.
- Incremental indexing: after changes, the repository reindexes only touched files and graph-adjacent artifacts that need refresh.
- Context preparation uses implemented capabilities, with semantic search only
  when configured and verified. No universal AST/graph/vector sequence is required.

## Required Artifact Contract

The downstream JSON artifacts must provide at least:

- `manifest.json` - schema version, tool version, commit identity, engine identity, generation timestamp, and artifact inventory.
- `files.json` - indexed files, language classification, fingerprints, and index status.
- `symbols.json` - symbol identities, kinds, source ranges, parent relationships, and module ownership.
- `edges.json` - call, import, reference, containment, and dependency edges between indexed symbols.
- `chunks.json` - symbol-level or chunk-level retrieval units. Optional
  embedding payloads/references must identify actual provider behavior; if no
  provider is configured, document semantic retrieval as unavailable/disabled.

The runtime may additionally persist raw tool-native artifacts, for example:

- `code-intel/index/scip/index.scip`
- `code-intel/index/ast-grep/`

These raw artifacts are optional supplements. They do not replace the mandatory normalized JSON contract.

The artifact schema can evolve, but these logical responsibilities must remain stable unless the baseline is intentionally migrated.
The generated JSON artifacts are required runtime outputs, but they must not be committed to git by downstream repositories.
Downstream repositories should ignore `code-intel/index/` and any raw tool-native artifact directories beneath that tree.

## Repo-Local Runtime Contract

In indexed mode, implement and document the applicable commands from:

- `python code-intel.py index`
- `python code-intel.py graph`
- `python code-intel.py embeddings` (optional; document whether it only prepares
  chunk records or actually integrates a provider)
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
- agents can use text search for focused lookups, validation and unindexed assets,
- agents must document stale or missing index coverage as `Evidence not available` when the index cannot support a requested analysis.

Downstream indexed rollout discipline:

- apply the baseline through the smallest repo-local surface that works first,
- keep the first rollout focused on `code-intel.py`, repo-local config, ignore rules, and `docs/architecture/code-intelligence.md`,
- Do not add extra downstream docs, tests, or planning artifacts unless the repository explicitly asks for them or existing repository contracts require them.

## Relationship to Future Capabilities

`code-intel/` is intentionally extensible.
Indexed mode starts with documented symbols/artifacts; adjacent capabilities
are optional and must demonstrate useful coverage.
Adjacent repository-local capabilities, such as generated C4 diagrams or other code-navigation assets, may live under the same control surface as long as they preserve the selected indexed contract.

## Transition Note

This revision replaces universal custom-index requirements with explicit basic
and indexed modes. Existing pinned/local contracts remain effective until a
reviewed migration updates the revision, selection/rationale and verification.
Do not remove working indexing/telemetry automatically. The shared runner's
SCIP/Tree-sitter implementation remains available and its CLI/schema is not
changed by this policy revision.

The bundled `embeddings` command prepares records with null vectors and `query`
uses substring matching; a semantic provider/vector retrieval is not bundled.
Document those limits instead of claiming a complete semantic pipeline.

## Role Boundaries

- `SWE` owns architecture and implementation of the code-intelligence baseline.
- `QA` owns verification that the entrypoint, JSON artifacts, and incremental-update behavior work as documented.
- `SRE` owns reproducible execution in CI or containerized release paths and the operational handling of caches or generated artifacts.
