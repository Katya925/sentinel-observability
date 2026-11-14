# ============================================================
# SENTINEL OBSERVABILITY
# CONFIGURACIÓN DE TRAZAS OPENTELEMETRY
# ============================================================

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor
)


def configurar_tracing(app):

    # Identificar el servicio que genera las trazas
    resource = Resource.create({
        "service.name": "sentinel-backend",
        "service.version": "1.0.0",
        "deployment.environment.name": "educational-local"
    })

    provider = TracerProvider(resource=resource)

    # Dirección del receptor OTLP de Tempo
    endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://tempo:4317"
    )

    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=True
    )

    processor = BatchSpanProcessor(exporter)

    provider.add_span_processor(processor)

    # Registrar el proveedor global
    trace.set_tracer_provider(provider)

    # Instrumentar automáticamente las solicitudes FastAPI
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        excluded_urls="/health,/metrics"
    )

    return trace.get_tracer("sentinel.observability")