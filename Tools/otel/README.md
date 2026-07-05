# OTEL Pattern for Python

Use this when a Python repository needs the minimum OpenTelemetry baseline from this guidelines repo without inventing its own setup from scratch.

This folder is a reusable pattern, not a requirement to create a runtime dependency on `Guidelines`.

## What Is Shared vs Local

Keep these concerns shared:

- OpenTelemetry resource construction,
- OTLP trace endpoint normalization,
- env-based OTEL settings loading,
- minimal trace exporter setup for `http/protobuf`.

Keep these concerns local to the product repository:

- framework instrumentation,
- logging format and log shipping,
- metrics implementation,
- service naming defaults,
- deployment environment wiring.

## Recommended Adoption Model

Preferred:

1. copy or vendor `Tools/otel/telemetry.py` into the product repository
2. add a thin repo-local wrapper around it
3. keep framework-specific instrumentation in that wrapper

Temporary bootstrap option:

1. load `Tools/otel/telemetry.py` from this repository
2. replace that dependency with a repo-local copy before treating it as production baseline

The goal is a stable product repository that owns its runtime wiring while reusing the same OTEL contract.

## Shared OTLP Contract

Every repository using this pattern should support:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

## Minimal Product-Repo Wrapper

```python
from telemetry import configure_tracing, load_settings_from_env


def setup_telemetry() -> None:
    settings = load_settings_from_env("my-service")
    configure_tracing(
        service_name=settings.service_name,
        service_version=settings.service_version,
        environment=settings.environment,
        endpoint=settings.endpoint,
        protocol=settings.protocol,
        instrumentors=[],
    )
```

Replace `instrumentors=[]` with repo-local framework hooks such as FastAPI, Flask, Django, Celery, or internal runtime instrumentation.

## Python Scope

This helper is intentionally Python-specific.
Non-Python repositories should keep the same OTLP contract but implement the runtime locally or add a language-specific helper.

## Runtime Guarantees

- If `OTEL_EXPORTER_OTLP_ENDPOINT` is empty, service attribution is still configured but no exporter is attached.
- If `OTEL_EXPORTER_OTLP_PROTOCOL` is not `http/protobuf`, this helper raises and expects a repo-local implementation instead.
- Collector base URLs are normalized to a trace export URL ending in `/v1/traces`.
