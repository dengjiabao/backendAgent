from typing import Any


async def collect_public_events(result: dict[str, Any]) -> list[dict[str, Any]]:
    """将运行结果转换为可公开的状态事件，不输出隐藏推理。"""

    events: list[dict[str, Any]] = [{"type": "run_started", "run_id": result.get("run_id")}]
    if result.get("tool"):
        events.append({"type": "tool_result", "tool": result["tool"], "data": result.get("data", [])})
    if result.get("action"):
        arguments = result.get("arguments", {})
        events.append({"type": "tool_proposed", "tool": result["action"], "parameter_keys": list(arguments)})
    if result.get("citations"):
        events.append({"type": "citation", "citations": result["citations"]})
    if result.get("status") == "waiting_approval":
        events.append({"type": "approval_required", "approval_id": result.get("approval_id")})
    events.append({"type": "final", "result": result})
    return events
