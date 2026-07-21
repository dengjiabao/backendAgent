import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from ecommerce_agent.security.redaction import redact


@dataclass
class Span:
    name: str
    attributes: dict[str, Any]
    started_at: float = field(default_factory=time.perf_counter)
    duration_ms: float = 0.0


class InMemoryTracer:
    """独立模式 Trace 实现，生产环境可替换为 OpenTelemetry Exporter。"""

    def __init__(self) -> None:
        self.spans: list[Span] = []

    @contextmanager
    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Iterator[Span]:
        safe_attributes = {
            key: "[已脱敏]"
            if any(secret in key.lower() for secret in ("key", "token", "password", "authorization", "cookie"))
            else redact(value)
            if isinstance(value, str)
            else value
            for key, value in (attributes or {}).items()
        }
        span = Span(name, safe_attributes)
        try:
            yield span
        finally:
            span.duration_ms = (time.perf_counter() - span.started_at) * 1000
            self.spans.append(span)


class MetricsRegistry:
    def __init__(self) -> None:
        self._values: dict[str, float] = {}

    def inc(self, name: str, value: float = 1.0) -> None:
        self._values[name] = self._values.get(name, 0.0) + value

    def snapshot(self) -> dict[str, float]:
        return dict(self._values)
