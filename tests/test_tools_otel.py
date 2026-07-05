from pathlib import Path
import importlib.util
import sys


def _load_shared_otel():
    module_path = Path("Tools/otel/telemetry.py")
    spec = importlib.util.spec_from_file_location("shared_otel", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_resource_includes_service_identity():
    module = _load_shared_otel()

    resource = module.build_resource(
        service_name="investor",
        service_version="abc1234",
        environment="prod",
    )

    assert resource.attributes["service.name"] == "investor"
    assert resource.attributes["service.version"] == "abc1234"
    assert resource.attributes["deployment.environment"] == "prod"


def test_trace_endpoint_appends_v1_traces_suffix():
    module = _load_shared_otel()

    endpoint = module.build_trace_export_endpoint("https://otel-collector.example.com")

    assert endpoint == "https://otel-collector.example.com/v1/traces"


def test_trace_endpoint_keeps_explicit_signal_path():
    module = _load_shared_otel()

    endpoint = module.build_trace_export_endpoint("https://otel-collector.example.com/v1/traces")

    assert endpoint == "https://otel-collector.example.com/v1/traces"


def test_load_settings_from_env_uses_defaults_and_env(monkeypatch):
    module = _load_shared_otel()

    monkeypatch.setenv("OTEL_SERVICE_VERSION", "55aa086")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://otel-collector.example.com")
    monkeypatch.setenv("DEPLOYMENT_ENVIRONMENT", "production")

    settings = module.load_settings_from_env(default_service_name="guidelines")

    assert settings.service_name == "guidelines"
    assert settings.service_version == "55aa086"
    assert settings.protocol == "http/protobuf"
    assert settings.endpoint == "https://otel-collector.example.com"
    assert settings.environment == "production"


def test_configure_tracing_without_endpoint_skips_exporter(monkeypatch):
    module = _load_shared_otel()

    events = {}

    class FakeTracerProvider:
        def __init__(self, resource):
            self.resource = resource
            self.span_processors = []

        def add_span_processor(self, processor):
            self.span_processors.append(processor)

    monkeypatch.setattr(module, "TracerProvider", FakeTracerProvider)
    monkeypatch.setattr(module, "_set_tracer_provider", lambda provider: events.setdefault("provider", provider))

    def fail_if_exporter_created(**kwargs):
        raise AssertionError("exporter must not be created without endpoint")

    monkeypatch.setattr(module, "OTLPSpanExporter", fail_if_exporter_created)

    provider = module.configure_tracing(
        service_name="guidelines",
        service_version="55aa086",
        environment="dev",
        endpoint="",
        protocol="http/protobuf",
    )

    assert provider is events["provider"]
    assert provider.span_processors == []
    assert provider.resource.attributes["service.name"] == "guidelines"


def test_configure_tracing_with_endpoint_adds_http_exporter(monkeypatch):
    module = _load_shared_otel()

    events = {}

    class FakeTracerProvider:
        def __init__(self, resource):
            self.resource = resource
            self.span_processors = []

        def add_span_processor(self, processor):
            self.span_processors.append(processor)

    class FakeOTLPSpanExporter:
        def __init__(self, endpoint=None):
            events["exporter_endpoint"] = endpoint

    class FakeBatchSpanProcessor:
        def __init__(self, exporter):
            self.exporter = exporter

    monkeypatch.setattr(module, "TracerProvider", FakeTracerProvider)
    monkeypatch.setattr(module, "OTLPSpanExporter", FakeOTLPSpanExporter)
    monkeypatch.setattr(module, "BatchSpanProcessor", FakeBatchSpanProcessor)
    monkeypatch.setattr(module, "_set_tracer_provider", lambda provider: events.setdefault("provider", provider))

    provider = module.configure_tracing(
        service_name="guidelines",
        service_version="55aa086",
        environment="prod",
        endpoint="https://otel-collector.example.com",
        protocol="http/protobuf",
    )

    assert provider is events["provider"]
    assert events["exporter_endpoint"] == "https://otel-collector.example.com/v1/traces"
    assert len(provider.span_processors) == 1
