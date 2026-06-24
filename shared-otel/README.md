# Shared OTEL Helper

Reusable OpenTelemetry baseline for Python product repositories.

## Purpose

Keep the repository-specific details local:

- framework instrumentation choices,
- service-specific naming defaults,
- deployment environment wiring,
- project-level logging and metrics conventions.

Move shared behavior here:

- OpenTelemetry resource construction,
- OTLP trace endpoint normalization,
- env-based OTEL settings loading,
- minimal tracer/exporter setup for `http/protobuf`,
- a reusable runtime contract that aligns with this repository's observability baseline.

## Expected Product-Repo Wrapper

Each Python product repository can keep a thin local wrapper that:

1. resolves the `Guidelines` repository via `GUIDELINES_REPO` or a sibling `../Guidelines`
2. loads `shared-otel/telemetry.py`
3. calls `load_settings_from_env(...)`
4. passes repo-local framework instrumentors into `configure_tracing(...)`

## Shared OTLP Contract

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

## Python Scope

This helper is intentionally Python-specific.
Non-Python repositories should still follow the same observability contract, but keep their implementation local or add a language-specific helper later.

## Runtime Behavior

- If `OTEL_EXPORTER_OTLP_ENDPOINT` is empty, tracing attribution is still configured but no exporter is attached.
- If `OTEL_EXPORTER_OTLP_PROTOCOL` is not `http/protobuf`, this shared helper raises and expects the product repository to provide its own implementation.
- The helper normalizes collector base URLs to a trace export URL ending in `/v1/traces`.
