# Code Intelligence Runner

Reusable code-intelligence runner logic for product repositories that want a consistent AST index without copying the same parsing, artifact, and CLI wiring into every repo.

This runner is separate from `Tools/audits` because code intelligence is not a quality or security scanner.

## Primary Toolchain

The baseline toolchain is:

- `SCIP` for semantic symbols and graph edges when the downstream repository provides a language-specific indexer
- `ast-grep` for AST-structural matching and chunk hints
- `rg` for text fallback and operator validation
- Tree-sitter fallback runtime only when `SCIP` is not configured or parity is still missing for the active language

`Tools/code-intel/` is therefore a thin orchestration layer around external tools plus a fallback parser, not a monolithic custom indexer.

## Consumption Model

Keep repository-specific details local:

- `code-intel/config/index.yaml`
- indexed language enablement and include/exclude paths
- `SCIP` indexer commands per enabled language
- embedding provider wiring and thresholds
- graph policies and project-specific symbol filters
- report, cache, or artifact retention decisions

Move shared behavior here:

- runtime selection and fallback ordering
- containerized execution model
- container image build inputs
- default JSON artifact layout
- raw tool artifact layout
- manifest generation and revision tracking
- incremental reindex orchestration
- consistent command construction for index, graph, embeddings, and config inspection

## Expected Product-Repo Integration

Each product repository should:

1. keep `code-intel.py` and repo-local `code-intel/`
2. keep project-specific settings in `code-intel/config/index.yaml`
3. document the project-specific implementation in `docs/architecture/code-intelligence.md`
4. consume `Tools/code-intel/` as the lower-level runtime behind the repo-local entrypoint
5. keep `code-intel/` separate from `audits/`

Root `tree-sitter.py` or `ast-index.py` entrypoints are not part of this baseline model.

## Expected Product-Repo Files

- `code-intel/config/index.yaml`
- `code-intel/index/manifest.json`
- `code-intel/index/files.json`
- `code-intel/index/symbols.json`
- `code-intel/index/edges.json`
- `code-intel/index/chunks.json`
- `docs/architecture/code-intelligence.md`

Recommended `code-intel/config/index.yaml` baseline:

```yaml
engine: scip
image: guidelines-code-intel:local
languages:
  - python
  - typescript
include:
  - src
  - tests
exclude:
  - node_modules
  - dist
  - coverage
incremental: true
tools:
  scip:
    enabled: true
    indexers:
      python: scip-python index
  ast_grep:
    enabled: true
  ripgrep:
    enabled: true
  fallback_tree_sitter:
    enabled: true
artifacts:
  index_dir: code-intel/index
```

`image` is the container image tag used by the shared runner.
`guidelines-code-intel:local` is the default local-build contract; downstream repositories may override it in `code-intel/config/index.yaml`.
`tools.scip.indexers` stays repo-local because `SCIP` indexers are language-specific.

## Default Runtime Contract

- `python code-intel.py index` builds or refreshes the AST and symbol index for the repository.
- `python code-intel.py graph` materializes symbol relationships such as calls, imports, containment, and references.
- `python code-intel.py embeddings` refreshes symbol-level or chunk-level retrieval units for semantic search.
- `python code-intel.py query <symbol-or-pattern>` performs a local symbol or pattern lookup for debugging and operator checks.
- `python code-intel.py config` prints resolved non-secret config and exits without rebuilding the index.

## Example Downstream Wrapper

Use a thin repo-local wrapper and keep `Tools/code-intel/` in the `Guidelines` repository:

```python
from pathlib import Path
import os
import sys


def _resolve_guidelines_root(repo_root: Path) -> Path:
    explicit = os.getenv("GUIDELINES_REPO")
    candidates = [Path(explicit)] if explicit else []
    candidates.append(repo_root.parent / "Guidelines")
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "Tools" / "code-intel" / "code_intel_runner.py").exists():
            return resolved
    raise SystemExit("Cannot resolve Guidelines repository.")


repo_root = Path(__file__).resolve().parent
guidelines_root = _resolve_guidelines_root(repo_root)
sys.path.insert(0, str(guidelines_root / "Tools" / "code-intel"))

from code_intel_runner import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], repo_root=repo_root))
```

The repository contains the same example as a standalone file in `Tools/code-intel/example_code_intel.py`.

## Build The Image

Build the local shared runtime image from this repository root:

```bash
docker build -t guidelines-code-intel:local Tools/code-intel
```

If a downstream repository wants a heavier Python and TypeScript starter profile, build the optional indexer target:

```bash
docker build --target indexers -t guidelines-code-intel:indexers Tools/code-intel
```

If a downstream repository wants a separate heavy profile for Java and C#, build the JVM/.NET target:

```bash
docker build --target indexers-jvm-dotnet -t guidelines-code-intel:indexers-jvm-dotnet Tools/code-intel
```

The image uses:

- `Tools/code-intel/Dockerfile`
- `Tools/code-intel/requirements.txt`
- `Tools/code-intel/runtime/`

The base image currently installs:

- `scip v0.9.0`
- fallback Python runtime dependencies
- `ast-grep`
- `rg`

The `scip` CLI is installed from the official `scip-code/scip` release binaries.
The runtime uses `scip print --json` when it needs to normalize a binary `index.scip` into repo-local JSON artifacts and no cached JSON sidecar is already present.

Downstream repositories may extend the image or inject extra tooling when their enabled languages require specific `SCIP` indexers.

Optional indexer profile:

- `docker build --target indexers ...` adds `Node 20`
- that target installs `@sourcegraph/scip-python`
- that target installs `@sourcegraph/scip-typescript`
- `Node 20` is used because the current official `scip-typescript` support window is Node 18 or Node 20, while `scip-python` requires Node 16 or newer
- downstream repositories that want this profile can point `code-intel/config/index.yaml` at `guidelines-code-intel:indexers` instead of `guidelines-code-intel:local`

Optional JVM/.NET indexer profile:

- `docker build --target indexers-jvm-dotnet ...` adds `Java 17`
- that target adds `.NET 8`
- that target installs `scip-java 0.12.3` via Coursier bootstrap, following the official `scip-java` local install path
- that target installs `scip-dotnet 0.2.14` via `dotnet tool install --global`, following the official `scip-dotnet` local install path
- downstream repositories that want this profile can point `code-intel/config/index.yaml` at `guidelines-code-intel:indexers-jvm-dotnet`

Current runtime scope:

- runtime configuration can select `SCIP` first, then Tree-sitter fallback when no configured indexer exists for the active languages
- primary normalized artifact coverage today still comes from the Tree-sitter fallback path
- fallback language support covers `python`, `javascript`, `typescript`, `tsx`, and `json`
- fallback symbol extraction covers modules, functions, classes, methods, and TypeScript interfaces
- fallback graph extraction covers contain edges, import edges, resolved internal calls, and simple external call edges
- chunk generation is available at symbol granularity

Migration status:

- raw `SCIP` artifact path is reserved at `code-intel/index/scip/index.scip`
- normalized `SCIP` decode currently prefers `code-intel/index/scip/index.scip.json` and otherwise falls back to `scip print --json`
- raw `ast-grep` artifact path is reserved under `code-intel/index/ast-grep/`
- minimal `SCIP` normalization now produces modules, functions, classes, interfaces, contain edges, import edges, and reference edges
- full `SCIP` normalization into richer relationships and call edges is not complete yet
- downstream repositories should treat Tree-sitter fallback as the parity path until `SCIP` normalizers reach feature completeness

## Local Prerequisites

- Docker installed
- Docker daemon running
- repo-local source tree or generated assets already prepared if the repository depends on them for parsing

## Runtime Behavior

- the shared runtime uses `SCIP + ast-grep + rg` as the primary toolchain contract
- the shared runtime allows Tree-sitter fallback when `SCIP` indexers are unavailable or incomplete for the active languages
- the shared runtime reads repo-local `code-intel/config/index.yaml`
- the shared runtime image executes `python -m runtime.cli`
- the shared runtime writes JSON artifacts to `code-intel/index/`
- the shared runtime may also write raw tool-native artifacts under `code-intel/index/scip/` and `code-intel/index/ast-grep/`
- the shared runtime records schema, engine, and revision identity in `manifest.json`
- the shared runtime supports incremental refresh for touched files and affected graph edges
- the shared runtime exposes a simple CLI entrypoint through `code_intel_runner.main(...)`
- the shared runtime returns non-zero exit status on parse, configuration, or artifact-write failure so CI can fail deterministically
