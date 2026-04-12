# Root Cause Analysis Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Bug ID
- Related Commit/PR

## Required Sections

1. Incident Context
2. Timeline
3. Technical Findings
4. Root Cause Statement
5. Contributing Factors
6. Fix Strategy
7. Preventive Actions
8. Decision Log

## Analysis Rules

- Analysis must be based on facts: code, logs, metrics, traces, configurations.
- Root cause must be stated as a causal chain, not as a symptom.
- Each hypothesis must have a status: `confirmed` / `rejected` / `unknown`.
- Conclusions must be separated from assumptions; assumptions must be explicit.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- One primary root cause and its technical mechanism are documented.
- System factors are identified: process, monitoring, test gaps, config.
- Explain why the defect was not caught earlier.
- Selected fix includes trade-off rationale.
- Preventive actions are defined with owner and due date.

## Template

```md
# Root Cause Analysis - <RCA-ID>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Bug ID: <BUG-NNNN>
Related Commit/PR: <link/id>

## 1. Incident Context
...

## 2. Timeline
- <time>: ...

## 3. Technical Findings
- Fact 1:
- Fact 2:

## 4. Root Cause Statement
...

## 5. Contributing Factors
- ...

## 6. Fix Strategy
- ...

## 7. Preventive Actions
- Action: ...
- Owner: ...
- Due Date: ...

## 8. Decision Log
- ...
```