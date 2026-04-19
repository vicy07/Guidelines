# Feature Flow Example

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

### Input (Requirement)

```json
{
  "id": "feature_1",
  "description": "Add user login",
  "acceptance_criteria": [
    "User can log in with email/password",
    "Invalid credentials are rejected"
  ]
}
```

### SWE Output

```json
{
  "tasks": [
    {
      "id": "task_1",
      "type": "backend",
      "description": "Implement login API"
    }
  ]
}
```

### QA Output

```json
{
  "tests": [
    "valid login",
    "invalid login"
  ]
}
```

### SRE Output

```json
{
  "deployment": "success"
}
```
