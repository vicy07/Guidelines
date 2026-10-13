# Test Strategy Format Standard

Version: 1.6.0
Owner: Repository Maintainer
Last Updated: 2026-10-14

## Metadata (required)

- Version
- Owner
- Last Updated
- Release Scope
- Related Requirements Version
- Related Security Guidelines Version

## Required Sections

1. Testing Objectives
2. Risk Profile
3. Test Levels and Scope
4. Environment Strategy
5. Test Data Strategy
6. Automation Strategy
7. Security Testing
8. Entry and Exit Criteria
9. Quality Gates
10. Traceability (requirements/use cases/security controls -> tests)

## Strategy Rules

- Map existing entry/exit criteria and quality gates to the shared DoD in
  `guidelines/playbooks/delivery-policy.md`; record product-specific additions
  without duplicating the canonical checklist.

- Strategy is driven by risks and scenario criticality, not by available tools.
- Separate fast PR/push checks, risk-triggered checks, approved schedules, and
  release gates using `guidelines/playbooks/ci-verification-policy.md`. Do not
  require SonarQube or full audit/scanner suites on every CI event.
- Document selection rules, evidence age/invalidation, failure ownership, and
  a feedback-time budget. Release gates may reuse fresh candidate evidence;
  missing, stale, or skipped required evidence is not a passing result.
- Every key use case must have explicit coverage level (`Unit`, `Integration`, `E2E`).
- NFRs must be covered by dedicated checks with measurable thresholds.
- Responsibility boundaries between test levels must be explicit and non-overlapping.
- Security checks must align with `Areas/swe/security-guidelines.md`.
- Verify diagnostic coverage for the selected profile from
  `Areas/requirements/repository-profiles.md`; verify OTLP only when export is used.
  Critical paths require signal/alert and recovery evidence.
- Verify representative navigation/change-impact tasks for the chosen
  basic/indexed mode. In indexed mode, also verify entrypoint, JSON artifacts,
  coverage/freshness and incremental updates. Do not equate a populated index
  or null embedding fields with working semantic retrieval.
- The strategy must verify SBOM inventory coverage, component criticality/risk rules, EOL evidence freshness, dependency/architecture drift, and lifecycle gate behavior defined by `Areas/swe/component-lifecycle-guidelines.md`.
- If evidence is missing, explicitly state `Evidence not available`.

## Quality Checklist

- Testing goals and success criteria are defined.
- Each risk has a mapped test type and execution frequency.
- There is a minimum smoke/regression set for CI.
- Test environments and test data management rules are documented.
- Diagnostic checks cover profile-required signals and selected export behavior;
  library/CLI tests confirm host control and no automatic background telemetry.
- Navigation checks prove adequacy for representative tasks; indexed checks
  additionally verify manifest/file/symbol/edge/chunk artifacts against scope.
- Lifecycle checks cover missing/invalid/stale SBOM data, EOL and near-EOL components, unknown evidence, architectural inventory drift, and expired exceptions.
- Release requires a mandatory security baseline (SAST/SCA and critical auth/authz checks).
- Quality gates have measurable thresholds and a `go/no-go` rule.

## Template

```md
# Test Strategy - <Product/Release>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Release Scope: <release/sprint>
Related Requirements Version: <x.y>
Related Security Guidelines Version: <x.y>

## 1. Testing Objectives
...

## 2. Risk Profile
- Risk:
- Impact:
- Mitigation:

## 3. Test Levels and Scope
- Unit: ...
- Integration: ...
- E2E: ...
- Non-functional: ...

## 4. Environment Strategy
...

## 5. Test Data Strategy
...

## 6. Automation Strategy
...

## 7. Security Testing
- SAST: ...
- SCA: ...
- Auth/AuthZ: ...

## 8. Entry and Exit Criteria
...

## 9. Quality Gates
...

## 10. Traceability
...
```
