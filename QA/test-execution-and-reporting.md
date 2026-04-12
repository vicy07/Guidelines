# Test Execution and Reporting Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Strategy Version
- Build/Release ID

## Required Sections

1. Execution Plan
2. Smoke and Critical Path Run
3. Regression Run
4. Defect Handling Rules
5. Result Reporting
6. Release Decision (Go/No-Go)
7. Post-Release Validation

## Execution Rules

- Execution starts with smoke checks for critical scenarios.
- Regression starts only after smoke passes.
- Each case result is recorded as `passed` / `failed` / `blocked`.
- Every `blocked` or `failed` case must include issue link and owner.
- Final report must include `go/no-go` decision and open risks.

## Reporting Rules

- Report must include total cases, pass rate, defect leakage, and critical failures.
- Non-functional tests must report actual metrics against target thresholds.
- Release status is based on quality gates, not subjective assessment.

## Quality Checklist

- Smoke, regression, and critical NFR checks are completed.
- All critical defects have status and action plan.
- No undocumented deviations from the test plan.
- `go/no-go` decision is recorded and agreed.
- Post-release sanity checks are completed in a production-like environment.

## Template

```md
# Test Execution Report - <Build/Release>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Strategy Version: <x.y>
Build/Release ID: <id>

## 1. Execution Plan
...

## 2. Smoke and Critical Path Run
- Result: <passed|failed|blocked>
- Evidence: ...

## 3. Regression Run
- Total:
- Passed:
- Failed:
- Blocked:

## 4. Defect Handling Rules
- ...

## 5. Result Reporting
- Pass Rate: ...
- Critical Failures: ...
- Defect Leakage: ...

## 6. Release Decision (Go/No-Go)
- Decision: <go|no-go>
- Rationale: ...
- Open Risks: ...

## 7. Post-Release Validation
- ...
```