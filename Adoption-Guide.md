# Adoption Guide

## Purpose

Explain how to attach this guidelines repository to new and existing product repositories with the least disruptive path that still creates a usable agentic-development baseline.

## Applicability Selection

Before adding tooling, select a profile and `basic`/`indexed` navigation mode
using `Areas/requirements/repository-profiles.md`. Record owner and rationale
in `.governance/baseline.yaml`; retain the existing revision pins. Basic mode
keeps a short navigation record in product documentation without a custom AST
pipeline. Docs-only repositories keep scope/ownership/verification in README.

Existing pinned baselines and stricter local controls remain in force until a
reviewed adoption change records the new revision, selection, affected controls
and evidence. Missing selection does not authorize deleting working tooling or
telemetry. `check-product-baseline` keeps its legacy eight-document check when
the adoption block is absent; it checks declarations and static presence, not
runtime quality, security, observability or retrieval accuracy.

## Recommended Adoption Model

Use one of two tracks:

1. New project bootstrap
2. Existing project retrofit

Do not force the same rollout shape on both.

## Track 1: New Project Bootstrap

For a new repository:

1. Select the profile and create the applicable structure from
   `Product-Repository-Blueprint.md`; docs-only repositories avoid product scaffolding.
2. Add `AGENTS.md` with direct links to the `Guidelines` engineering baseline,
   the adopted baseline documents, and the companion
   [`AI-Governance`](https://github.com/vicy07/AI-Governance) operating model.
   Preferred form: public GitHub links for both repository reference points and
   the primary baseline documents.
3. Product repositories create the minimum documents under `docs/requirements/`,
   `docs/`, `docs/qa/` and `docs/sre/`, including a short navigation-mode record
   at `docs/architecture/code-intelligence.md`. Docs-only repositories record
   scope, ownership and verification in README instead.
4. Add `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`. Keep fast
   PR/push checks separate from scheduled scanners and release gates using
   `guidelines/playbooks/ci-verification-policy.md`.
5. Add `audits.py`, repo-local `audits/` scanner wiring, `audits/config/sonar-project.properties`, `audits/config/trivy.yaml`, `audits/config/components.yaml`, and the tracked enriched SBOM at `audits/sbom/components.cdx.json`.
6. For indexed mode, add `code-intel.py`, repo-local `code-intel/` and
   `code-intel/config/index.yaml` separately from `audits.py`. Basic mode uses
   existing navigation/search tools and a short documentation record.
7. Reuse `Tools/audits/` as the primary local audit entrypoint and add the repo-specific `audits/scanners/components.py` adapter. Do not add root `sonar.py`, `trivy.py`, or `components.py` entrypoints as part of the baseline model.
8. Indexed mode may reuse `Tools/code-intel/` and its reference
   `SCIP + ast-grep + rg` stack; choose supported language tools and document
   actual coverage/fallbacks. Basic mode does not need this runtime.
9. Implement profile-appropriate diagnostics and alerts; document an OTLP
   contract only when OTLP export is used. Libraries leave exporter setup to the host.
10. Implement the visible line `Last commit: <localized date/time> | <short sha>` in the product UI if the product is user-facing.
11. Add reviewed `docs/releases/X.Y.Z.md` files to the release workflow. If the solution has a web page, add an accessible release-notes page and link it from primary navigation or the required footer/status line.

This is the preferred path because it avoids later migration overhead.

## Track 2: Existing Project Retrofit

For an existing repository, do not rewrite the whole structure unless the current layout is already failing delivery.

Recommended sequence:

1. Inventory current docs, tests, workflows, and deployment scripts. Record
   the selected profile/mode and migration impact before relaxing any existing control.
2. Map existing files to the target baseline before creating new ones.
3. Add only the missing minimum artifacts.
4. Normalize CI, deploy, SonarQube, Trivy, component license and lifecycle/EOL, code-intelligence, and observability gates before attempting broader documentation cleanup.
5. When an audit is run, create exactly one consolidated
   `docs/audits/YYYY-MM-DD-<scope>.md` report for that work item. Include the
   exact `Guidelines` version pinned by commit hash and commit date, all required
   EOL, Trivy, security, and GDPR/privacy rows, and an explicit reason for every
   `not-run` or `not-applicable` check.
6. Add the visible last-commit line without changing unrelated architecture.
7. Add versioned release notes before the release artifact is built; for web solutions, publish and link the release-notes page without changing unrelated architecture.
8. Move toward the target structure incrementally as files are naturally touched.

## Practical Proposal for Existing Projects

Use a three-step rollout:

### Step 1: Control Surface

Add:

- `AGENTS.md` with direct links to `Guidelines` and `AI-Governance`
- prefer public GitHub links over local machine-specific paths

Outcome:

- agents can discover the governing baseline quickly,
- repositories avoid unnecessary governance scaffolding when a lightweight reference is enough.

### Step 2: Delivery Gates

Add or normalize:

- CI workflow with fast change checks, documented risk triggers, separate
  approved scanner schedules, and candidate-evidence rules from
  `guidelines/playbooks/ci-verification-policy.md`,
- deploy workflow or release workflow,
- release record linking goals/Issues/PRs, immutable version/revision and
  environment, verification/rollback, and independent notification status;
  reuse an existing release/runbook location and declare whether each Issue
  is accepted at merge or only after publication/runtime verification,
- exact notification runbook/entrypoint, no-send doctor, runtime configuration
  owner, private journal location and failure/reconciliation procedure;
  use the [homelab runbook](https://github.com/vicy07/homelab/blob/main/docs/release-notifications.md)
  for the AI-Governance personal Telegram channel without copying credentials,
- SonarQube integration,
- Trivy integration,
- component license and lifecycle/EOL monitoring, license type/evidence/risk, criticality/risk classification, and the tracked enriched SBOM,
- adequate basic navigation or justified indexed tooling with coverage/freshness evidence,
- profile-appropriate diagnostics/alerts and OTLP configuration when used,
- minimum smoke and regression checks.

Outcome:

- changes are gated before merge and release,
- repository health stops depending on manual memory.

### Step 3: Minimal Artifacts

For product profiles, create or align (docs-only scope uses README):

- `docs/requirements/mission.md`
- `docs/requirements/use-cases.md`
- `docs/requirements/user-flows.md`
- `docs/architecture.md`
- `docs/technical-architecture.md`
- `docs/architecture/code-intelligence.md`
- `docs/qa/test-strategy.md`
- `docs/sre/deployment-and-operations.md`
- `docs/releases/README.md` and `docs/releases/X.Y.Z.md` for every published version

Outcome:

- agents and humans share the same minimum context for delivery decisions.

Architecture documentation rule:

- keep `docs/architecture.md` short and navigational,
- keep `docs/technical-architecture.md` as the canonical technical design document,
- use `docs/architecture/` only for ADRs or deeper supporting architecture records when needed.

## Delivery Policy Adoption

Adopt [Delivery Policy and Definition of Done](guidelines/playbooks/delivery-policy.md)
with the [AI-Governance sequential execution contract](https://github.com/vicy07/AI-Governance/blob/main/.codex/AGENTS.md).
Map existing acceptance criteria, DoD, review/CI gates and release records before
adding files. Record the owning roadmap/tracker, task order/dependencies, acceptance
boundaries and authorized agent actions in the product's existing control surface.
Keep the shared policy linked; add product-specific DoD conditions in the existing
QA/delivery documentation. Pin adopted revisions through the existing baseline record.

Maintain releasable `main`, verify the merged revision, and record releases by
full SHA and applicable version/artifact digest. This model does not use GitHub
Releases. Declare whether task completion occurs at merge, publication or verified
deployment; retain open delivery work until its boundary passes. Docs-only adoption
uses existing README/task/PR records without adding product-document scaffolding.

## Integration Rules

- Reuse existing code and workflow conventions where they are already effective.
- For retrofits, prefer the narrowest practical repo-local surface that satisfies the baseline first.
- Do not expand the main README, docs index, or repo-wide tests during the first code-intelligence rollout unless the repository explicitly asks for it or an existing contract would otherwise fail.
- Do not rename stable directories just to match the blueprint if a mapping layer is enough.
- Prefer repo-local wrappers over copied logic, prefer `Tools/audits/` over separate per-tool orchestration when the repository uses multiple scanners, consider `Tools/code-intel/` when indexed mode is selected, keep `code-intel.py` separate from `audits.py`, keep `SCIP` language-indexer commands in repo-local config, and do not add root `sonar.py`, `trivy.py`, or `components.py` in the baseline model.
- Persist the current component inventory, license expression/type/evidence and risk, lifecycle evidence, criticality, and risk in `audits/sbom/components.cdx.json`; assess license compatibility during architecture design before adoption and refresh it at least weekly and when dependencies, component versions, architecture, build/linking/packaging or distribution models, runtime/base images, or external-provider contracts change.
- In indexed mode, generated `code-intel/index/` artifacts are required runtime outputs, but they must not be committed to git; downstream repositories should ignore that tree and rebuild it locally or in CI when needed.
- If evidence for a rule is missing, document `Evidence not available` instead of inventing compliance.
- Keep scanner JSON, SARIF, logs, and SBOMs as linked machine evidence, but do
  not split one audit work item into multiple human Markdown reports. Follow
  `guidelines/playbooks/audit-reporting-standard.md`. Do not start the audit
  suite implicitly as part of normal delivery or QA.

## Root AGENTS Reference Template

Use this minimal control surface in a downstream product repository and add
only product-specific instructions below it:

```md
# Repository instructions

This repository adopts:

- Engineering and documentation baseline:
  https://github.com/vicy07/Guidelines
- Repository structure:
  https://github.com/vicy07/Guidelines/blob/main/Product-Repository-Blueprint.md
- Adoption rules:
  https://github.com/vicy07/Guidelines/blob/main/Adoption-Guide.md
- Agent workflow and handoffs:
  https://github.com/vicy07/AI-Governance

Adopted Guidelines revision: <commit SHA>

Product-specific instructions may specialize the shared baselines. Record any
intentional deviation explicitly.
```

Use a commit SHA when reproducibility matters, especially for an audit or a
regulated delivery. Keep the repository links as stable discovery points even
when a revision is pinned.

Copy `templates/governance-baseline.yaml` to
`.governance/baseline.yaml`, replace both revision placeholders with full commit
SHAs, select `adoption.profile` and `adoption.code_intelligence`, and replace
owner/rationale placeholders. Check the repository with:

```bash
npm run check-product-baseline -- /path/to/product --strict
```

Omit `--strict` during an incremental retrofit to report gaps without failing
the command. Enable strict mode in CI after the mapped minimum artifacts exist.

## Suggested Consumption Pattern

The lightest workable integration for most teams is:

1. Add `AGENTS.md` that points to `Guidelines` and
   [`AI-Governance`](https://github.com/vicy07/AI-Governance).
   Preferred form: public GitHub repository links plus direct GitHub links to
   the primary engineering baseline documents.
2. Create the product minimum docs set, or README-based docs-only scope/verification.
3. Wire CI and deploy workflows.
4. Reuse `Tools/audits/` as the primary local audit entrypoint for SonarQube, Trivy, and the repo-local component scanner.
5. Keep `Tools/sonar/` and `Tools/trivy/` as lower-level reusable runners behind `Tools/audits/`, and keep lifecycle-source adapters repo-local, not as root entrypoints.
6. Document basic navigation or implement justified indexed mode with
   `code-intel.py`, `code-intel/` and coverage/freshness checks; the shared
   runtime is optional. Keep generated indexes out of git.
7. Define the profile-appropriate diagnostic path. When OTLP is used, document
   its configuration; Python projects may copy/vendor `Tools/otel/telemetry.py`.
8. If an audit is performed, save one consolidated
   `docs/audits/YYYY-MM-DD-<scope>.md` report using
   `guidelines/playbooks/audit-reporting-standard.md`, including the `Guidelines`
   commit hash and commit date used for the review. This step is opt-in and
   requires an explicit audit request or approved schedule.
9. Add the visible last-commit line.
10. Add reviewed versioned release notes. For web solutions, expose the generated release-notes page through primary navigation or the required footer/status line.

That gives a usable baseline without forcing a full repository redesign on day one.
