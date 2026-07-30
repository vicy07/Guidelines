# Consolidated Audit Reporting Standard

Version: 1.1.0
Owner: Repository Maintainer
Last Updated: 2026-07-30

## Purpose

Define one durable, decision-ready report for each repository audit run. Scanner
outputs may remain separate machine artifacts, but the human audit result must
not be fragmented across per-tool or per-role Markdown reports.

## Explicit-Invocation Rule

- Repository-wide audit execution is opt-in. It starts only from an explicit
  audit request, an approved scheduled audit, or a human running it locally.
- Normal delivery, code review, QA, release verification, security-sensitive
  work, and documentation review must not implicitly start the full audit suite.
- Assign one `Audit Operator` for the run. This may be a dedicated audit or
  reviewer/security agent, or a named human performing the audit locally.
- `QA` may consume audit evidence for a release decision, but does not own or
  execute the repository-wide audit by default.
- The Audit Operator owns report completeness, evidence traceability, status
  consistency, and the audit gate recommendation. The operator requests focused
  SWE, SRE, QA, BA, privacy, or legal input only when the audit evidence requires
  it; those roles are not an automatic audit chain.
- Legal approval remains outside the AI audit unless an authorized legal
  reviewer is explicitly recorded.

## One-File Rule

- One audit work item or coordinated audit run produces exactly one consolidated
  Markdown report under `docs/audits/`.
- Name it `YYYY-MM-DD-<scope>.md`; for example,
  `docs/audits/2026-07-23-guidelines-compliance.md`.
- EOL/component lifecycle, Trivy, security, and GDPR/privacy must be represented
  in that file. Include other applicable checks such as SonarQube in the same
  file.
- Do not create separate human reports for individual tools, roles, remediation
  passes, or re-gates that belong to the same audit work item.
- A re-run for the same work item updates the same report and preserves a dated
  execution-history entry. A new audit work item creates a new dated file.
- Raw JSON, SARIF, logs, SBOMs, screenshots, and other machine evidence may be
  stored separately and linked from the consolidated report.

## Required Status and Method

Every required audit area must have exactly one current status:

- `passed`
- `failed`
- `blocked`
- `not-run`
- `not-applicable`

Every area must also identify its execution method:

- `tool/runner` for deterministic scanner or scripted evidence;
- `AI review` for evidence-based repository analysis;
- `manual review` for a named human review;
- `mixed` when more than one method was used.

`not-run` and `not-applicable` are explicit outcomes, not omissions. They must
include the exact reason, impact on the final gate, and an owner/follow-up when
the missing check is still required. Use `Evidence not available` when the
expected evidence cannot be found.

## Required Coverage

The consolidated report must contain a coverage row and a detailed subsection
for each of these areas:

1. Guidelines compliance
2. EOL and component lifecycle
3. Trivy filesystem scan
4. Trivy image scan
5. Security review
6. GDPR and privacy review

Add SonarQube, tests, deployment verification, or other checks when they are in
scope. Trivy image scanning may be `not-applicable` only when the repository
does not produce or deploy a container image and the report records that
evidence.

The GDPR/privacy section is an engineering and product-data gap assessment. An
AI review must not claim legal certification. At minimum it reviews, or records
why it could not review:

- personal-data inventory and data flows;
- purpose, lawful-basis assumptions, and data minimization;
- retention, deletion, and data-subject request paths;
- processors, transfers, cookies, tracking, and consent where applicable;
- privacy/security controls, documentation, and unresolved owner decisions.

## Evidence Contract

For `tool/runner` evidence, record:

- exact command, tool and version;
- audited target, commit SHA, and execution timestamp;
- exit code and interpreted result;
- durable artifact path or link.

For `AI review` or `manual review`, record:

- reviewed scope and evidence paths;
- checks or questions applied;
- findings and limitations;
- reviewer role and review timestamp.

Claims without evidence must be marked `Evidence not available`; they must not
be inferred as passing.

## Required Report Structure

```md
# Audit Report - <scope>

- Audit date: <YYYY-MM-DD>
- Repository: <owner/name>
- Audited commit: <full SHA>
- Audit work item: <issue/link>
- Guidelines baseline: <full SHA and commit date>
- Audit operator: <role/name or "manual local">
- Reviewers: <roles/names>

## Executive Summary
- Final gate: <go|no-go|conditional|blocked>
- Summary: <decision-ready result>

## Coverage Matrix
| Area | Method | Status | Evidence | Owner / follow-up |
|---|---|---|---|---|
| Guidelines compliance | AI review | <status> | <path/link> | <owner/action> |
| EOL and component lifecycle | tool/runner | <status> | <path/link> | <owner/action> |
| Trivy filesystem | tool/runner | <status> | <path/link> | <owner/action> |
| Trivy image | tool/runner | <status> | <path/link> | <owner/action> |
| Security | AI review | <status> | <path/link> | <owner/action> |
| GDPR and privacy | AI review | <status> | <path/link> | <owner/action> |

## Execution History
| Timestamp | Area | Command or review method | Result | Evidence |
|---|---|---|---|---|

## Detailed Results
### Guidelines Compliance
### EOL and Component Lifecycle
### Trivy Filesystem
### Trivy Image
### Security Review
### GDPR and Privacy Review

## Findings
| ID | Severity | Area | Finding and evidence | Status | Owner | Due |
|---|---|---|---|---|---|---|

## Exceptions and Accepted Risks
| ID | Rationale | Compensating control | Owner | Review / expiry |
|---|---|---|---|---|

## Not Run or Not Applicable
<Explicit reasons, gate impact, evidence, and follow-up. Write "None" when empty.>

## Final Gate
- Decision: <go|no-go|conditional|blocked>
- Rationale:
- Required follow-up:
```

## Completion Gate

The audit is not complete until:

- all required coverage areas appear in the one consolidated report;
- every area has method, status, evidence, and ownership;
- every missing execution is explicit;
- findings, exceptions, and re-runs are reconciled into the current status;
- the final gate is consistent with unresolved critical findings and missing
  required evidence.
