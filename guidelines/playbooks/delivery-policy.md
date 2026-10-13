# Delivery Policy and Definition of Done

Version: 1.0.0
Owner: QA Lead
Last Updated: 2026-10-14

## Purpose and Ownership

Define merge readiness, task completion, releasable `main`, and release identity.
PO/BA own acceptance criteria and the completion boundary. SWE owns coherent
changes, review corrections and revision traceability. QA owns the Definition
of Done (DoD), evidence interpretation and the quality decision. SRE owns
publication/deployment verification, rollback and operational readiness.

Agent task selection, sequential execution and handoffs are governed by
[AI-Governance](https://github.com/vicy07/AI-Governance/blob/main/.codex/AGENTS.md).
Check frequency and evidence reuse follow the
[CI Verification Policy](ci-verification-policy.md); this policy does not add
unconditional scanners, full audits, or a separate report for every task.

## Trigger and Inputs

Apply before merge, task closure, and release/promotion. Inputs are the owning
Issue and roadmap/dependencies, acceptance criteria and boundary, current
candidate revision, review results, applicable QA/CI evidence and release/runbook
records. Determine the repository profile using
[repository profiles](../../Areas/requirements/repository-profiles.md).

Acceptance criteria describe the task-specific outcome. DoD describes shared
quality conditions. The acceptance boundary states when completion is judged:
local verification, merge, publication, or verified deployment in a named
environment. Declare it before implementation; do not weaken it to close an Issue.

## Execution and Merge Readiness

1. Confirm scope, acceptance criteria, dependencies and completion boundary.
2. Implement a coherent change on a working branch. Local commits and draft
   PRs may be created during implementation; they do not assert completion.
3. Review the candidate for correctness, acceptance coverage, security and
   operational impact. Record the review method/result in the PR or existing
   task record; follow required reviewer/approval rules in the owning repository.
4. Resolve blocking review findings and satisfy the pre-merge DoD conditions
   below for the current candidate. Commit remaining changes and run affected
   checks again when their inputs changed.
5. Merge through the repository's PR workflow only after applicable checks and
   approvals pass. Preserve branch protections; do not bypass a failed gate.
6. Check the resulting `main` revision and its applicable CI. A branch check
   does not automatically prove the merged revision or built artifact valid;
   reuse evidence only under the CI Verification Policy's equivalence rules.
7. Reach the declared acceptance boundary, record its evidence, then close the
   task. Merge-scoped implementation can complete while a linked delivery Issue
   remains open for publication/runtime acceptance. An Issue requiring deployment
   itself stays open until deployment verification passes.

## Definition of Done

Before merge, satisfy these conditions for the merge scope. Before declaring
the task done, satisfy them for its full declared acceptance boundary:

- Acceptance criteria applicable at this boundary have direct evidence. All
  remaining publication/runtime criteria have an explicit owner and remain open.
- Review is complete, required approvals exist, and blocking findings are resolved.
- Applicable checks pass for the current candidate; evidence records command or
  check, result and checked revision/digest. Missing, stale, failed or mismatched
  required evidence blocks the applicable gate. Unselected checks have a policy
  reason; exceptions require the existing approved, owned, time-bounded process.
- Meaningful behavior changes have proportionate regression coverage. Explain
  when a new automated test is unnecessary; do not add tests that only repeat prose.
- Affected requirements, design, QA, deployment and operations documentation is
  updated, or the task record explains why no update is required.
- Issue, PR and immutable commit/artifact identities are linked. Known limitations,
  accepted risks and follow-up work have explicit ownership; follow-ups cannot
  silently replace an unmet acceptance criterion.
- The declared completion boundary has been reached and verified. Publication
  and deployment require their applicable release gates and recovery/rollback
  readiness; runtime acceptance includes checks in the named environment.
- The final handoff records results, evidence, remaining obligations and the next
  step, with reusable learning assessed under AI-Governance.

Use the existing Issue/PR, QA strategy and release/runbook records for evidence.
Product repositories may extend this DoD and map it to effective existing
locations. Record intentional deviations explicitly; do not silently drop gates.

## Releasable Main

`main` contains integrated, verified, logically complete changes and is maintained
in a releasable state. Unfinished functionality is allowed only when safely
isolated, for example by a disabled feature flag, with existing behavior verified
and its completion work tracked. Do not merge diagnostic-only or partial changes
that require another fix to restore supported behavior.

A failed protected-branch check makes the resulting revision unverified. Stop
promotion and dependent delivery; prioritize a corrective change or rollback
through the documented workflow, then verify the recovered revision. Never
report the failing revision as release-ready.

Releasable does not mean already deployed, and each merge need not be a release.
Several completed tasks may form one logical release; pending required release
checks must still pass before promotion.

## Release Identity and Acceptance

A release is a logically complete set of changes that passed its required checks
and is recorded by full Git commit SHA, plus a version when used and an immutable
artifact digest when applicable. A version must resolve to that immutable identity;
a branch name or moving tag alone is insufficient. GitHub Releases are not used
by this delivery model; creating a GitHub Release is not a completion gate.

The release record links the outcome, Issues/PRs, identity, required boundary,
verification, limitations and applicable rollback/recovery reference. Reuse the
existing record or the
[AI-Governance release template](https://github.com/vicy07/AI-Governance/blob/main/templates/release.md).
Record publication, deployment verification and notification delivery separately;
merge, tag creation or notification success cannot establish runtime acceptance.
For docs-only work, a verified revision may be the release boundary; for a service,
record the revision/artifact actually deployed and the runtime checks required.

## Outputs, Exit Criteria and Escalation

Outputs are a reviewed PR/change, evidence tied to the resulting revision, and
an updated owning task/release record. Exit only when the declared boundary and
DoD are satisfied. No product-document scaffolding is required for docs-only work.

A failed gate or unmet criterion keeps the relevant task open. Record the blocker,
owner and next action. Escalate ambiguous scope/ownership to PO/BA, quality/evidence
questions to QA/SWE, and publication/recovery risk to SRE. A blocked task may yield
to independent ready work under AI-Governance; it must not be reported as done.
