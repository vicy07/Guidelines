# Audit Runtime

Reusable audit runner logic for product repositories that want one local entrypoint for multiple scanners without duplicating Docker, reporting, and CLI wiring.

Runner outputs are machine evidence, not separate human audit conclusions. For
each audit work item, link all applicable runner evidence from exactly one
`docs/audits/YYYY-MM-DD-<scope>.md` report and combine it with the required
security and GDPR/privacy reviews. Follow
`guidelines/playbooks/audit-reporting-standard.md`; record an explicit `not-run`
or `not-applicable` result when a required runner was not executed. Do not run
this suite automatically as part of ordinary QA or delivery unless a repository
explicitly configures an approved scheduled audit.

## Scope

Shared behavior lives here:

- scanner CLI dispatch
- Docker availability checks
- Docker container execution helpers
- predictable report file generation
- Trivy scanner orchestration
- Sonar scanner orchestration through `Tools/sonar`
- extension dispatch for a repo-local component scanner that enriches and checks downstream SBOM license and lifecycle evidence

Repository-specific behavior stays local:

- scanner defaults such as project key, coverage paths, and image references
- local config files such as `audits/config/trivy.yaml`, `.trivyignore`, `audits/config/sonar-project.properties`, and `audits/config/components.yaml`
- license/lifecycle-source adapters, architecture/third-party discovery, license and criticality assignments, and `audits/sbom/components.cdx.json`
- package scripts and repo-facing wrapper commands

## Recommended Structure In Product Repositories

Keep a thin local layer:

- `audits.py`
- `audits/config/trivy.yaml`
- `audits/config/components.yaml`
- `audits/config/sonar-project.properties`
- `audits/sbom/components.cdx.json`
- `audits/scanners/components.py`
- `audits/scanners/trivy.py`
- `audits/scanners/sonar.py`

Root `sonar.py`, `trivy.py`, and `components.py` entrypoints are not part of this baseline model.

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
- `python audits.py components scan`
- `python audits.py components check`
- `python audits.py all`

Trivy execution is Docker-only and does not require a local `trivy` binary on `PATH`.

The downstream scanner mapping and `all_plan` must include the repo-local `components` scanner. `scan` refreshes authoritative license and lifecycle evidence and writes the enriched tracked SBOM; `check` validates schema, completeness, freshness, license and lifecycle risk gates, and drift without treating missing evidence as permissive, compatible, or supported. The normative contract is `Areas/swe/component-lifecycle-guidelines.md`.
