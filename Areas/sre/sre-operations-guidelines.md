# SRE Operations Guidelines

Version: 1.4.0
Owner: SRE Lead
Last Updated: 2026-07-12

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
- Every repository must define an observability baseline that includes logs, metrics, traces, and an OTLP contract appropriate to the repository type.
- Critical services require logs, metrics, tracing, and alerts before release.
- Every release path must include rollback readiness.
- Production application releases must originate from committed Git state and run through the repository's documented Git-based delivery workflow.
- Agents and operators must not publish application code directly through a hosting-platform CLI, UI, or API. This prohibition includes direct deploy, redeploy, upload, and code-replacing service mutations (for example, `railway up` or an equivalent platform command).
- Hosting-platform tools may be used read-only for diagnostics, logs, status, and post-deploy verification. Runtime configuration changes and emergency operations require their own documented, auditable path and must not be used to bypass Git-based code delivery.
- Release readiness gates must include Trivy filesystem scanning before merge and container-image scanning before promotion when the repository produces deployable images.
- Release readiness and CI must include a reproducible code-intelligence path for `code-intel.py`, preferably through a containerized shared runtime, when the repository baseline requires indexed artifacts.
- Runtime configuration changes must be auditable.
- SRE documentation must publish exact OTLP client-facing endpoint patterns for external, in-cluster, and local runtime paths when those paths exist.
- Frontend or static-web repositories must document the client telemetry ingestion path and how it correlates with backend or platform telemetry.
- Library and CLI repositories must document the host-runtime observability expectations and the fallback behavior when OTLP export is unavailable.
- SRE handover must publish the exact Trivy entrypoints, thresholds, and suppression-record location used by the release path.
- SRE handover must publish the exact code-intelligence entrypoints, artifact location, cache/update model, and the commit-association rules used for generated index artifacts.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Reliability objectives are defined and owned.
- Alerting coverage exists for critical user-impact paths.
- Observability coverage and OTLP configuration are documented for the repository type.
- Code-intelligence execution and artifact freshness rules are documented for CI or release automation.
- Trivy scan coverage and release thresholds are documented for applicable artifact types.
- Rollback and recovery paths are validated.
- Production release evidence identifies the Git commit and the Git-based workflow that published it; no direct platform publication was used.
- Release readiness decision includes operational risk notes.

## OTLP Endpoint Handover Pattern

When a repository or platform exposes an OpenTelemetry Collector, document client configuration in env form, not only as prose.

Recommended handover blocks:

External OTLP/HTTP:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

Internal Docker or service-mesh OTLP/HTTP:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

Internal gRPC:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
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

## Trivy Release Gate Handover Pattern

Recommended release-gate entrypoints:

Filesystem baseline:

```text
python audits.py trivy scan
```

Deployable container image baseline:

```text
python audits.py trivy image ghcr.io/example/service:${GIT_SHA}
```

Required operator notes:

- Default repository thresholds should fail on `HIGH` and `CRITICAL` findings unless an approved repository-specific policy says otherwise.
- Accepted suppressions must be traceable to an owner, ticket, and review/expiry point.
- If a repository does not ship a deployable image, document that boundary explicitly in the release path.

## Code Intelligence Handover Pattern

Recommended repository entrypoints:

```text
python code-intel.py index
python code-intel.py graph
```

Required operator notes:

- The baseline code-intelligence toolchain is `SCIP + ast-grep + rg`; Tree-sitter may remain only as a documented fallback path.
- The preferred execution model is a containerized shared runtime rather than a manual host installation path.
- Generated artifacts should include commit or revision identity in `code-intel/index/manifest.json` so downstream automation can detect stale indexes.
