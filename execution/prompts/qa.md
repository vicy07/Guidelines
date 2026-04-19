Input: task.json
Output: test.json

Rules:
- output must be valid JSON only
- output must be a single JSON object that conforms to execution/schemas/test.json
- include both happy-path and edge-case coverage in ordered steps
- no markdown, no comments, no extra keys

Exact Output Example:
{
  "id": "TEST-001",
  "task_id": "TASK-001",
  "type": "integration",
  "steps": [
    "Submit valid credentials and verify successful authentication.",
    "Submit invalid credentials and verify access is denied without token issuance."
  ],
  "expected_result": "Valid credentials authenticate successfully; invalid credentials are rejected."
}