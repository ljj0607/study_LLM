import sqlite3
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

"""" 长期记忆,断点续存 """

# 1、创建checkpointer
conn = sqlite3.connect('./langgraph_sqlite', check_same_thread=False)
checkpointer = SqliteSaver(conn)

class MyState(TypedDict, total=False):
    key_1: str
    key_2: str
    key_3: str

def node_1(state: MyState) -> MyState:
    print("node_1")
    return {"key_1":"value_1"}
    return {"key_1":"value_1"}

def node_2(state: MyState) -> MyState:
    print("node_2")
    # raise ValueError("node_2 故意报错")
    return {"key_2":"value_2"}

def node_3(state: MyState) -> MyState:
    print("node_3")
    return {"key_3":"value_3"}

builder = StateGraph(MyState)

builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)


config = {"configurable":{"thread_id": "123"}}
graph = builder.compile(checkpointer=checkpointer)

try:
    # # 第一次故障
    # res = graph.invoke({}, config)
    # 断点恢复，
    res = graph.invoke(None, config)    # None这次不传新的输入，直接从上一次的 checkpoint 继续恢复执行
    print(res)
except Exception as e:
    print(f"第一次失败：{type(e).__name__}: {e}")
