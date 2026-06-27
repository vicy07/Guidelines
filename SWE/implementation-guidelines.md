# Implementation Guidelines

Version: 1.3.0
Owner: SWE Lead
Last Updated: 2026-06-27

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related QA Strategy Version

## Required Sections

1. Implementation Scope
2. Module Ownership
3. Coding Standards
4. Dependency Management
5. Change Traceability
6. Technical Debt Handling
7. Handover to QA/SRE

## Rules

- Every change must map to an explicit module owner.
- Behavior changes must be traceable to requirements/use cases.
- Architectural boundaries must not be bypassed for convenience.
- Temporary fixes must include debt records and closure criteria.
- Every repository must implement its repository-type observability path and document the exact OTLP contract used for attribution or export.
- Every repository must implement a repository-local Trivy entrypoint for filesystem scanning, and repositories that produce deployable container images must also define an image-scanning entrypoint before release.
- Backend and service repositories must emit logs, metrics, and traces from the running service.
- Frontend or static-web repositories must emit client telemetry and error events through a documented telemetry path that preserves OpenTelemetry-compatible correlation.
- Library and CLI repositories must emit structured logs and document how OpenTelemetry attribution or export is enabled when embedded or executed in target runtimes.
- Implementation handover must include the exact Trivy invocation path, config file location, and the ownership record for any accepted suppressions.
- Implementation handover must include the exact OTLP protocol and endpoint values expected in each runtime environment:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

- For user-facing projects, implementation must preserve the project's chosen technology and architecture while delivering the required visible status/footer line: `Last commit: <localized date/time> | <short sha>`.
- The deployed implementation must source that visible line from metadata that exists in the target runtime; do not assume a local `.git` checkout is available in production containers or hosted runtimes.
- If commit details are not available, keep the same visible line and render `Last commit: unavailable`.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Module ownership is explicit.
- Requirement-to-code traceability is documented.
- Security and reliability impacts are reviewed.
- Security scanning entrypoints and suppression ownership are documented.
- Observability and OTLP contract implications are documented for the repository type.
- QA handover includes test scope and risk notes.
- SRE handover includes deployment and observability implications.
