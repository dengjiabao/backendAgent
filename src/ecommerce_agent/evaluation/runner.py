import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvaluationReport:
    cases: int
    tool_accuracy: float
    security_accuracy: float
    average_latency_ms: float
    token_cost: float


class EvaluationRunner:
    """只接受注入的回答函数，评估测试不会触碰生产连接器。"""

    def __init__(self, answerer: Any) -> None:
        self.answerer = answerer

    async def run(self, path: str | Path) -> EvaluationReport:
        cases = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
        tool_hits = 0
        security_hits = 0
        latencies: list[float] = []
        token_cost = 0.0
        for case in cases:
            started = time.perf_counter()
            result = await self.answerer(case["question"])
            latencies.append((time.perf_counter() - started) * 1000)
            tool_hits += int(result.get("tool") == case.get("expected_tool"))
            security_hits += int(result.get("security") == case.get("expected_security"))
            token_cost += float(result.get("token_cost", 0.0))
        count = len(cases) or 1
        return EvaluationReport(
            len(cases),
            tool_hits / count,
            security_hits / count,
            sum(latencies) / count,
            token_cost,
        )
