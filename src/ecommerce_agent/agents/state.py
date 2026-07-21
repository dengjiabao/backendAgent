from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """节点之间传递的公开状态，不包含隐藏思维链。"""

    message: str
    plan: list[str]
    observations: list[dict[str, Any]]
    analysis: str
    answer: str
    citations: list[str]
    reflection: str
    run_id: str
    approval_id: str

