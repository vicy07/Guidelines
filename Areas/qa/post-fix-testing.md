# Post-Fix Testing Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Bug ID
- Fix Version/Build

## Required Sections

1. Test Scope
2. Test Environments
3. Targeted Verification (bug scenario)
4. Regression Coverage
5. Non-Functional Checks
6. Rollback Readiness
7. Exit Criteria

## Testing Rules

- First verify the original bug scenario in the same conditions where it occurred.
- After confirming the fix, run regression on related scenarios.
- For risky changes, include smoke + critical path checks.
- Every `failed` test must include issue/link and remediation status.
- Results must be recorded unambiguously: `passed` / `failed` / `blocked`.

## Quality Checklist

- Original defect is not reproducible on the target version.
- Related scenarios and dependencies are not broken.
- Negative and boundary cases for the changed area are verified.
- Monitoring and alerts show no degradation after deployment.
- A clear go/no-go decision and rollback plan exist.

## Template

```md
# Post-Fix Testing - <BUG-ID>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Bug ID: <BUG-NNNN>
Fix Version/Build: <version>

## 1. Test Scope
...

## 2. Test Environments
- ...

## 3. Targeted Verification (bug scenario)
- Case: ...
- Result: <passed|failed|blocked>
- Evidence: ...

## 4. Regression Coverage
- Case: ...
- Result: <passed|failed|blocked>

## 5. Non-Functional Checks
- ...

## 6. Rollback Readiness
- ...

## 7. Exit Criteria
- Release Decision: <go|no-go>
- Open Risks: ...
```