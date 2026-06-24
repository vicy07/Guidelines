from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Iterable

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ImportError:  # pragma: no cover - exercised indirectly through tests and fallback behavior
    class Resource:
        def __init__(self, attributes: dict[str, str]):
            self.attributes = attributes

        @classmethod
        def create(cls, attributes: dict[str, str]) -> "Resource":
            return cls(attributes)

    class _ProxyTracerProvider:
        pass

    class _FallbackTrace:
        def __init__(self) -> None:
            self._provider: Any = _ProxyTracerProvider()

        def get_tracer_provider(self) -> Any:
            return self._provider

        def set_tracer_provider(self, provider: Any) -> None:
            self._provider = provider

    trace = _FallbackTrace()

    class TracerProvider:
        def __init__(self, resource: Resource):
            self.resource = resource
            self.span_processors: list[Any] = []

        def add_span_processor(self, processor: Any) -> None:
            self.span_processors.append(processor)

    class BatchSpanProcessor:
        def __init__(self, exporter: Any):
            self.exporter = exporter

    class OTLPSpanExporter:
        def __init__(self, endpoint: str | None = None):
            self.endpoint = endpoint


Instrumentor = Callable[[Any], None]


@dataclass(frozen=True)
class TelemetrySettings:
    service_name: str
    service_version: str
    protocol: str
    endpoint: str
    environment: str


def build_resource(service_name: str, service_version: str = "", environment: str = "") -> Resource:
    attributes = {
        "service.name": str(service_name or "").strip() or "service",
    }
    if str(service_version or "").strip():
        attributes["service.version"] = str(service_version).strip()
    if str(environment or "").strip():
        attributes["deployment.environment"] = str(environment).strip()
    return Resource.create(attributes)


def build_trace_export_endpoint(endpoint: str) -> str:
    normalized = str(endpoint or "").strip().rstrip("/")
    if not normalized:
        return ""
    if normalized.endswith("/v1/traces"):
        return normalized
    return f"{normalized}/v1/traces"


def load_settings_from_env(
    default_service_name: str,
    *,
    default_service_version: str = "",
    environment_var: str = "DEPLOYMENT_ENVIRONMENT",
) -> TelemetrySettings:
    return TelemetrySettings(
        service_name=(os.getenv("OTEL_SERVICE_NAME") or default_service_name or "service").strip() or "service",
        service_version=(os.getenv("OTEL_SERVICE_VERSION") or default_service_version or "").strip(),
        protocol=(os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL") or "http/protobuf").strip() or "http/protobuf",
        endpoint=(os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or "").strip(),
        environment=(os.getenv(environment_var) or "").strip(),
    )


def _set_tracer_provider(provider: Any) -> Any:
    current_provider = trace.get_tracer_provider()
    if current_provider.__class__.__name__ == "ProxyTracerProvider":
        trace.set_tracer_provider(provider)
        return provider
    if current_provider.__class__.__name__ == "_ProxyTracerProvider":
        trace.set_tracer_provider(provider)
        return provider
    return current_provider


def configure_tracing(
    *,
    service_name: str,
    service_version: str = "",
    environment: str = "",
    endpoint: str = "",
    protocol: str = "http/protobuf",
    instrumentors: Iterable[Instrumentor] = (),
) -> Any:
    tracer_provider = TracerProvider(
        resource=build_resource(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
        )
    )

    normalized_endpoint = build_trace_export_endpoint(endpoint)
    normalized_protocol = str(protocol or "").strip() or "http/protobuf"

    if normalized_endpoint:
        if normalized_protocol != "http/protobuf":
            raise ValueError(
                f"Unsupported OTLP protocol for shared Python helper: {normalized_protocol}. "
                "Use http/protobuf or provide a repo-local implementation."
            )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=normalized_endpoint)
            )
        )

    active_provider = _set_tracer_provider(tracer_provider)
    for instrumentor in instrumentors:
        instrumentor(active_provider)
    return active_provider
