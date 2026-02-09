"""
Telemetry Module - OpenTelemetry tracing and metrics for agent pipeline.
Provides structured observability for all agent operations.
"""
import os
import structlog
from typing import Optional
from contextlib import contextmanager
import time

logger = structlog.get_logger()

# Check if OpenTelemetry is available
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None

# OTLP exporter (optional - requires opentelemetry-exporter-otlp)
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False
    OTLPSpanExporter = None


def init_telemetry(
    service_name: str = "proedit-agents",
    otlp_endpoint: Optional[str] = None
) -> None:
    """
    Initialize OpenTelemetry tracing.
    
    Args:
        service_name: Name of the service for tracing
        otlp_endpoint: Optional OTLP collector endpoint (e.g., "localhost:4317")
    """
    if not OTEL_AVAILABLE:
        logger.warning("opentelemetry_not_installed", 
            message="Install opentelemetry-sdk for tracing support")
        return
    
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
    })
    
    provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter if endpoint provided
    if otlp_endpoint and OTLP_AVAILABLE:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("telemetry_otlp_configured", endpoint=otlp_endpoint)
    
    trace.set_tracer_provider(provider)
    logger.info("telemetry_initialized", service=service_name)


def get_tracer(name: str = "proedit.agents"):
    """Get a tracer instance for creating spans."""
    if not OTEL_AVAILABLE:
        return None
    return trace.get_tracer(name)


class AgentSpan:
    """
    Context manager for tracing agent executions.
    Creates an OpenTelemetry span with structured attributes.
    """
    
    def __init__(
        self,
        agent_name: str,
        job_id: Optional[int] = None,
        model: Optional[str] = None,
        attempt: int = 1
    ):
        self.agent_name = agent_name
        self.job_id = job_id
        self.model = model
        self.attempt = attempt
        self.span = None
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        
        if OTEL_AVAILABLE:
            tracer = get_tracer()
            if tracer:
                self.span = tracer.start_span(f"agent.{self.agent_name}")
                self.span.set_attribute("agent.name", self.agent_name)
                if self.job_id:
                    self.span.set_attribute("job.id", self.job_id)
                if self.model:
                    self.span.set_attribute("model", self.model)
                self.span.set_attribute("attempt", self.attempt)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = (time.time() - self.start_time) * 1000
        
        if self.span:
            self.span.set_attribute("latency_ms", round(latency_ms, 2))
            
            if exc_type:
                self.span.set_attribute("error", True)
                self.span.set_attribute("error.type", exc_type.__name__)
                self.span.set_attribute("error.message", str(exc_val))
            
            self.span.end()
        
        # Always log via structlog regardless of OTEL
        if exc_type:
            logger.error(
                "agent_span_error",
                agent=self.agent_name,
                job_id=self.job_id,
                latency_ms=round(latency_ms, 2),
                error=str(exc_val)
            )
        else:
            logger.info(
                "agent_span_complete",
                agent=self.agent_name,
                job_id=self.job_id,
                latency_ms=round(latency_ms, 2)
            )
        
        return False  # Don't suppress exceptions
    
    def set_token_usage(self, input_tokens: int, output_tokens: int):
        """Record token usage for cost estimation."""
        if self.span:
            self.span.set_attribute("tokens.input", input_tokens)
            self.span.set_attribute("tokens.output", output_tokens)
            self.span.set_attribute("tokens.total", input_tokens + output_tokens)
    
    def set_cost_estimate(self, cost_usd: float):
        """Record estimated cost in USD."""
        if self.span:
            self.span.set_attribute("cost.usd", cost_usd)


# Initialize telemetry on module load if OTLP endpoint is configured
_otlp_endpoint = os.getenv("OTLP_ENDPOINT")
if _otlp_endpoint:
    init_telemetry(otlp_endpoint=_otlp_endpoint)
