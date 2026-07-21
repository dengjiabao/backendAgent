from ecommerce_agent.agents.state import AgentState


def planner_node(state: AgentState) -> AgentState:
    message = state.get("message", "")
    if any(word in message for word in ("订单", "商品", "库存", "售后")):
        plan = ["调用订单只读工具", "整理结果并引用来源"]
    else:
        plan = ["检索知识库证据", "整理结果并引用来源"]
    return {"plan": plan}


def analyst_node(state: AgentState) -> AgentState:
    count = len(state.get("observations", []))
    return {"analysis": f"已获得 {count} 条工具结果。"}


def reflection_node(state: AgentState) -> AgentState:
    answer = state.get("answer", "")
    citations = state.get("citations", [])
    if answer and not citations:
        return {"reflection": "需要补充依据。"}
    return {"reflection": "依据检查通过。"}
