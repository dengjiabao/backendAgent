from ecommerce_agent.agents.nodes import analyst_node, planner_node, reflection_node


def test_planner_creates_typed_plan_for_commerce_request():
    state = planner_node({"message": "查询订单状态"})
    assert state["plan"] == ["调用订单只读工具", "整理结果并引用来源"]


def test_analyst_summarizes_tool_observation_without_hidden_reasoning():
    state = analyst_node({"observations": [{"status": "paid"}]})
    assert state["analysis"] == "已获得 1 条工具结果。"


def test_reflection_rejects_unsupported_knowledge_answer():
    state = reflection_node({"answer": "订单已发货", "citations": []})
    assert state["reflection"] == "需要补充依据。"
