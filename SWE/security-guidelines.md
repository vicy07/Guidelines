# Security Guidelines Format Standard

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related Test Strategy Version

## Required Sections

1. Security Principles
2. Authentication and Authorization
3. Data Protection and Privacy
4. Secrets and Key Management
5. Secure Coding Rules
6. Dependency and Supply Chain Security
7. Logging, Monitoring, and Audit
8. Vulnerability Management
9. Security Review Checklist
10. Traceability (security controls -> tests)

## Security Rules

- Security controls are designed before feature implementation and documented explicitly.
- Least privilege is mandatory for users, services, and CI/CD.
- All input is treated as untrusted and must pass validation/normalization.
- Secrets must not be stored in code, repository history, or logs.
- Any security exception must be documented with owner and due date.

## Implementation Rules

- Use a centralized auth/authz mechanism without duplicating logic across modules.
- Errors must not expose internal system details.
- Dependency scanning and remediation of critical CVEs before release are mandatory.
- Critical actions must have an audit trail.
- If evidence is missing, explicitly state `Evidence not available`.

## Quality Checklist

- Security controls are defined for all critical scenarios.
- Access checks (role/resource/action) and negative auth cases are verified.
- Secure secret storage and rotation are in place.
- A SAST/SCA baseline and vulnerability response policy exist.
- Security controls are traceable to `QA/test-strategy.md` and release quality gates.

## Template

```md
# Security Guidelines - <Product>

Version: <x.y>
Owner: <name/role>
Last Updated: <YYYY-MM-DD>
Related Architecture Version: <x.y>
Related Test Strategy Version: <x.y>

## 1. Security Principles
...

## 2. Authentication and Authorization
...

## 3. Data Protection and Privacy
...

## 4. Secrets and Key Management
...

## 5. Secure Coding Rules
...

## 6. Dependency and Supply Chain Security
...

## 7. Logging, Monitoring, and Audit
...

## 8. Vulnerability Management
...

## 9. Security Review Checklist
...

## 10. Traceability
...
```