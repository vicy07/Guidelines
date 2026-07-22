# Audit Runtime

Reusable audit runner logic for product repositories that want one local entrypoint for multiple scanners without duplicating Docker, reporting, and CLI wiring.

## Scope

Shared behavior lives here:

- scanner CLI dispatch
- Docker availability checks
- Docker container execution helpers
- predictable report file generation
- Trivy scanner orchestration
- Sonar scanner orchestration through `Tools/sonar`
- extension dispatch for a repo-local EOL scanner that enriches and checks the downstream SBOM

Repository-specific behavior stays local:

- scanner defaults such as project key, coverage paths, and image references
- local config files such as `audits/config/trivy.yaml`, `.trivyignore`, `audits/config/sonar-project.properties`, and `audits/config/eol.yaml`
- lifecycle-source adapters, architecture/third-party discovery, criticality assignments, and `audits/sbom/components.cdx.json`
- package scripts and repo-facing wrapper commands

## Recommended Structure In Product Repositories

Keep a thin local layer:

- `audits.py`
- `audits/config/trivy.yaml`
- `audits/config/eol.yaml`
- `audits/config/sonar-project.properties`
- `audits/sbom/components.cdx.json`
- `audits/scanners/eol.py`
- `audits/scanners/trivy.py`
- `audits/scanners/sonar.py`

Root `sonar.py`, `trivy.py`, and `eol.py` entrypoints are not part of this baseline model.

That local layer should:

1. resolve the `Guidelines` repository via `GUIDELINES_REPO` or a sibling `../Guidelines`
2. add `Guidelines/Tools/audits` to `sys.path`
3. import `audits_runtime`
4. pass repo-local config into the shared scanner runners

## Runtime Contract

- `python audits.py trivy scan`
- `python audits.py trivy scan --format json`
- `python audits.py trivy image <image-ref>`
- `python audits.py sonar scan`
- `python audits.py eol scan`
- `python audits.py eol check`
- `python audits.py all`

Trivy execution is Docker-only and does not require a local `trivy` binary on `PATH`.

The downstream scanner mapping and `all_plan` must include the repo-local `eol` scanner. `scan` refreshes authoritative lifecycle evidence and writes the enriched tracked SBOM; `check` validates schema, completeness, freshness, risk gates, and drift without treating missing evidence as supported. The normative contract is `Areas/swe/component-lifecycle-guidelines.md`.
