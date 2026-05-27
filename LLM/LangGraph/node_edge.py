from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

"""
    动态决定下一步流转到哪个节点
"""
class GraphState(TypedDict):
    value: int
    step: str

def node_a(state: GraphState) -> dict:
    return {"value": state["value"], "step": "A执行完毕"}

def node_b(state: GraphState) -> dict:
    return {"value": state["value"] * 2, "step": "B执行完毕"}

def node_c(state: GraphState) -> dict:
    return {"value": state["value"] - 1, "step": "C执行完毕"}

# 只能返回"node_b"、"node_c"
def route_condition(state: GraphState) -> Literal["node_b", "node_c"]:
    """根据value值决定路由到哪个节点"""
    if state["value"] % 2 == 0:
        return "node_b"
    else:
        return "node_c"

def main():
    print("=== 条件边演示 ===")
    builder = StateGraph(GraphState)

    builder.add_node(node_a)
    builder.add_node(node_b)
    builder.add_node(node_c)

    builder.add_edge(START, "node_a")
    builder.add_conditional_edges(  # 路由映射
        "node_a",
        route_condition,
    )  #
    builder.add_edge("node_b", END)
    builder.add_edge("node_c", END)

    graph = builder.compile()
    result = graph.invoke({"value": 2})
    print(result)



if __name__ == "__main__":
    main()


