# Bug Verification Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Issue ID
- Severity (`S1`/`S2`/`S3`/`S4`)

## Required Sections

1. Problem Statement
2. Environment and Build
3. Preconditions
4. Reproduction Steps
5. Expected vs Actual
6. Evidence
7. Initial Impact Assessment

## Verification Rules

- Verification starts from reproducibility, not root-cause assumptions.
- Steps must be atomic, numbered, and repeatable.
- Environment must be explicit: app version, configuration, dependencies.
- Expected/Actual must describe observable behavior without interpretation.
- If the defect is not reproducible, state `Evidence not available` and what was checked.

## Quality Checklist

- Defect reproduced at least 2 times under the same conditions.
- Exact input data and time markers are recorded.
- Evidence exists: log, stack trace, screenshot, video, or request/response.
- Preliminary impact level on user and business is defined.
- Severity is assigned with concise rationale.

## Template

```md
# Bug Verification - <BUG-ID>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Issue ID: <BUG-NNNN>
Severity: <S1|S2|S3|S4>

## 1. Problem Statement
...

## 2. Environment and Build
...

## 3. Preconditions
...

## 4. Reproduction Steps
1. ...
2. ...

## 5. Expected vs Actual
Expected:
- ...

Actual:
- ...

## 6. Evidence
- ...

## 7. Initial Impact Assessment
- ...
```