Input: requirement.json
Output: task.json

Rules:
- output must be valid JSON only
- output must be a single JSON object that conforms to execution/schemas/task.json
- break work into minimal independent tasks by emitting one task per invocation
- include delivery risk context implicitly in the description field
- no markdown, no comments, no extra keys

Exact Output Example:
{
  "id": "TASK-001",
  "requirement_id": "REQ-001",
  "description": "Implement login endpoint with credential validation and rate-limit safeguards.",
  "type": "feature",
  "estimate": 3
}