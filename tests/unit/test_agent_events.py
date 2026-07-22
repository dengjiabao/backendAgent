import asyncio

from ecommerce_agent.agents.events import collect_public_events


def test_event_stream_exposes_status_tools_citations_and_final_only():
    result = {"run_id": "run-1", "type": "commerce", "tool": "order.list", "data": []}
    events = asyncio.run(collect_public_events(result))
    assert [event["type"] for event in events] == ["run_started", "tool_result", "final"]
    assert "data" in events[1]


def test_event_stream_marks_approval_required():
    result = {"run_id": "run-2", "status": "waiting_approval", "approval_id": "a-1", "action": "product.update", "arguments": {"id": "p-1"}}
    events = asyncio.run(collect_public_events(result))
    assert any(event["type"] == "approval_required" for event in events)
    assert any(event["type"] == "tool_proposed" for event in events)
