from ecommerce_agent.observability.otel import InMemoryTracer, MetricsRegistry


def test_tracer_records_span_attributes_without_secret_values():
    tracer = InMemoryTracer()
    with tracer.start_span("tool.execute", {"tool": "order.list", "api_key": "secret"}):
        pass
    span = tracer.spans[0]
    assert span.name == "tool.execute"
    assert span.attributes["api_key"] == "[已脱敏]"
    assert span.duration_ms >= 0


def test_metrics_registry_counts_runs_and_failures():
    metrics = MetricsRegistry()
    metrics.inc("agent_runs")
    metrics.inc("agent_runs")
    metrics.inc("agent_failures")
    assert metrics.snapshot() == {"agent_runs": 2.0, "agent_failures": 1.0}
    assert "agent_runs 2.0" in metrics.prometheus_text()
