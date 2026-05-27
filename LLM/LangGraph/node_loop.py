from typing import Annotated, Dict, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError

class LoopState(TypedDict):
    count: int
    result: str
    max_count: int

def node_a(state: LoopState) -> dict:
    new_count = state["count"] + 1
    return {
        "count": new_count,
        'result': f"已处理{new_count}次"  # 显示新值
    }

def node_b(state: LoopState) -> dict:
    return {'result': f"已处理{state['count']}次 - 辅助处理"}

# 只能返回b、END
def route(state: LoopState) -> Literal["node_b", END]:
    """条件路由函数：决定是继续循环还是终止"""
    if state['count'] >= state['max_count']:
        return END
    else:
        return "node_b"



builder = StateGraph(LoopState)
builder.add_node(node_a)
builder.add_node(node_b)

builder.add_edge(START, "node_a")
builder.add_conditional_edges("node_a", route)
builder.add_edge("node_b", "node_a") # 环链接

graph = builder.compile()
try:
    res = graph.invoke(input={
        "count": 0,
        'result': '',
        'max_count': 300
    }, config={
        'recursion_limit': 600 # 设置递归限制
    })
    print(res)

except GraphRecursionError as e:
    print(f"递归错误: {e}")




