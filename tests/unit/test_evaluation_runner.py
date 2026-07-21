import asyncio
import json

from ecommerce_agent.evaluation.runner import EvaluationRunner


def test_evaluation_runner_records_tool_and_security_metrics(tmp_path):
    path = tmp_path / "golden.jsonl"
    path.write_text(
        json.dumps({"question": "查询订单", "expected_tool": "order.list", "expected_security": "allow"}) + "\n",
        encoding="utf-8",
    )

    async def answer(question):
        return {"tool": "order.list", "security": "allow"}

    report = asyncio.run(EvaluationRunner(answer).run(path))
    assert report.cases == 1
    assert report.tool_accuracy == 1.0
    assert report.security_accuracy == 1.0
