# CI Verification Policy

Version: 1.0.0
Owner: QA Lead
Last Updated: 2026-10-13

## Purpose and Ownership

Keep feedback fast while preserving evidence for merge and release decisions.
QA owns check selection, thresholds, and evidence interpretation. SWE owns
change-impact mapping and reproducible checks. SRE owns schedules, alerts,
release enforcement, and workflow operation. BA/PO validate business impact
when a critical user journey changes.

This policy defines execution frequency. Tool integration requirements in the
Blueprint do not require running every installed scanner on every CI event.

## Execution Matrix

| Trigger | Required scope | Expensive checks |
|---|---|---|
| Pull request and protected-branch push | Deterministic install; applicable format/lint/type/build checks; affected unit/integration tests and minimum smoke regression; cheap validation of applicable config and committed SBOM | No full audit, SonarQube, full Trivy scan, network EOL refresh, full E2E/performance suite, or full code-index rebuild by default |
| Relevant change | Checks for changed dependency manifests/lockfiles, images, infrastructure, auth/authz, sensitive data paths, scanner policy, or architecture boundaries | Run the applicable dependency, secret, configuration, security, lifecycle, or integration check when the documented trigger matches; do not invoke the entire audit suite |
| Approved schedule | Repository health, vulnerabilities, lifecycle evidence, quality trends, and broader regression | SonarQube and full filesystem/security scans on the documented cadence; EOL evidence refresh at least weekly; broader suites according to risk |
| Release or promotion | Candidate build/smoke evidence, applicable security/quality/lifecycle gates, rollback readiness | Consume fresh evidence for the candidate; run missing, stale, or invalidated checks; scan the deployable image by immutable digest |
| Explicit audit request | Scope agreed for that audit | Run the requested audit and use the consolidated audit-reporting standard |

Documentation-only changes require applicable documentation/reference checks.
Treat executable documentation, generator inputs, CI configuration, and files
consumed at runtime according to their actual impact, not just their extension.
When impact cannot be determined, run the relevant broader verification and
record why. Security-sensitive changes require targeted security verification.

## SonarQube and Scanner Cadence

- SonarQube and full audit/scanner suites must not be unconditional steps in
  ordinary PR/push CI. Configure them in separate scheduled, manually invoked,
  or explicitly triggered workflows/jobs.
- Default starting cadence for supported codebases: weekly SonarQube and full
  filesystem/security scans. SRE and QA must document a shorter interval for
  exposed or higher-risk services, plus failure ownership and response time.
  This interval is a team baseline, not a vendor requirement.
- Targeted SonarQube analysis may be selected by a documented risk trigger or
  requested review. Configure new-code quality conditions where supported;
  new-code gates do not prove that the scanner processes only changed files.
- Scheduled failures create an owned remediation record/alert. They are not
  retroactively reported as a passed or failed PR execution. Known blocking
  findings remain blockers for the applicable release gate.
- A scanner integration, a security review, or a release is not authorization
  to invoke `python audits.py all`. Full audits remain explicitly invoked
  under `audit-reporting-standard.md`.

## Evidence Reuse and Gate Integrity

Each repository must document trigger/path mapping, owner, command, thresholds,
maximum evidence age, invalidation rules, and failure/exception handling in its
existing QA strategy and deployment/release documentation.

- Evidence must identify the checked commit or immutable artifact digest,
  command/tool version, relevant configuration, result, and timestamp; include
  vulnerability/lifecycle data freshness where applicable.
- Reuse evidence only for the same inputs and applicable policy. Changes to
  source, dependency locks, runtime/base image, scanner configuration/rules,
  or relevant vulnerability/lifecycle data invalidate affected evidence.
  A different commit requires a recorded equivalence check for those inputs.
- Release evidence must satisfy the documented maximum age and required
  security/quality/lifecycle thresholds. Missing, failed, stale, or mismatched
  required evidence blocks promotion unless an owned, time-bounded exception
  is explicitly approved. A skipped scan is never a passing scan.
- Cheap CI checks may validate committed SBOM schema, freshness, drift, risk,
  and exception expiry without fetching lifecycle data or regenerating the
  whole inventory on every push. Inventory changes require the relevant
  refresh; scheduled refresh catches changes without source edits.
- Record intentionally unselected checks as `not-run` with the policy reason
  in the CI summary; ordinary delivery does not need a full audit report.
- Keep an always-reported required CI status. Conditional jobs must report
  their selection outcome; filtering an entire required workflow must not
  leave branch protection waiting indefinitely or report a skipped gate as
  verified. Apply merge-queue checks when the repository uses a merge queue.

## Feedback Cost

- Define a repository-specific feedback budget and measure p50/p95 duration,
  queue time, reruns, flaky failures, and time to an actionable result. Evidence
  not available: no runtime saving is claimed until measurements exist.
- Use job-level impact selection, dependency/tool caches, and cancellation of
  superseded PR runs. Do not cancel an active production promotion as if it
  were disposable CI.
- Avoid duplicate expensive runs for branch push and PR events. Reuse results
  only under the evidence rules above; release validation may need a new run
  for the actual merge commit or artifact.
- Batch related edits before expensive verification. Retry or broaden checks
  when a changed candidate, failure, or uncovered risk warrants it; never
  impose a one-run limit that prevents necessary verification.
