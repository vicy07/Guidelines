# SRE Operations Guidelines

Version: 1.0.0
Owner: SRE Lead
Last Updated: 2026-04-12

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related QA Execution Version

## Required Sections

1. Reliability Objectives
2. Observability Baseline
3. Release Readiness Gates
4. Rollback Strategy
5. Runtime Configuration Controls
6. Capacity and Performance Controls
7. Operations Checklist

## Rules

- Reliability objectives must be explicit and measurable.
- Critical services require logs, metrics, tracing, and alerts before release.
- Every release path must include rollback readiness.
- Runtime configuration changes must be auditable.
- When OTLP ingestion is used, SRE documentation must publish exact client-facing endpoint patterns for external, in-cluster, and local runtime paths.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Reliability objectives are defined and owned.
- Alerting coverage exists for critical user-impact paths.
- Rollback and recovery paths are validated.
- Release readiness decision includes operational risk notes.

## OTLP Endpoint Handover Pattern

When a repository or platform exposes an OpenTelemetry Collector, document client configuration in env form, not only as prose.

Recommended handover blocks:

External OTLP/HTTP:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

Internal Docker or service-mesh OTLP/HTTP:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

Internal gRPC:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

Signal-specific OTLP/HTTP fallback:

```dotenv
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otel-collector.example.com/v1/traces
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://otel-collector.example.com/v1/metrics
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=https://otel-collector.example.com/v1/logs
```

Required operator note:

- If the SDK follows the OTLP/HTTP specification, `OTEL_EXPORTER_OTLP_ENDPOINT` should be the base URL and the SDK will append `/v1/traces`, `/v1/metrics`, and `/v1/logs`.
