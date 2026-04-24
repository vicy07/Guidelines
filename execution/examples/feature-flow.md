# Feature Flow Example

Version: 1.1.0
Owner: Repository Maintainer
Last Updated: 2026-04-24

## Reference Chain

- Canonical artifact chain lives in `execution/examples/chain-login-v1/`.
- This folder demonstrates `raw_request -> requirement -> tasks -> test_report -> release`.

## Input (Requirement)

```json
{
  "id": "REQ-0001",
  "title": "User login",
  "description": "Users can authenticate with email and password to access protected account features.",
  "acceptance_criteria": [
    "Valid credentials return success and session token.",
    "Invalid credentials return an authentication error."
  ],
  "priority": "high"
}
```

## SWE Output (Task Bundle)

```json
{
  "requirement_id": "REQ-0001",
  "tasks": [
    {
      "id": "TASK-0001",
      "requirement_id": "REQ-0001",
      "title": "Implement POST /auth/login endpoint",
      "type": "feature",
      "estimate_points": 5,
      "status": "done"
    }
  ]
}
```

## QA Output (Test Report)

```json
{
  "id": "TEST-0001",
  "requirement_id": "REQ-0001",
  "task_ids": ["TASK-0001"],
  "summary": "Login checks passed.",
  "checks": [
    {"name": "Valid credentials", "status": "pass"}
  ],
  "verdict": "pass"
}
```
