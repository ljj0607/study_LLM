import operator
import sqlite3

from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# 创建 checkpoint
connection = sqlite3.connect("./langgraph_sqlite", check_same_thread=False)
checkpointer = SqliteSaver(connection)

class State(TypedDict):
    """ 状态类型定义 """
    aggregate: Annotated[list, operator.add]

def a(state: State, config):
    print(f"a-{state["aggregate"]}")
    return {"aggregate": ["A"]}

def b(state: State, config):
    print(f"b-{state['aggregate']}")
    return {"aggregate": ["B"]}

def b_2(state: State, config):
    print(f"b-2-{state['aggregate']}")
    return {"aggregate": ["B_2"]}

def c(state: State, config):
    print(f"c-{state['aggregate']}")
    return {"aggregate": ["C"]}

def d(state: State, config):
    print(f"d-{state['aggregate']}")
    return {"aggregate": ["D"]}

# 创建图形
builder = StateGraph(State)

# 创建节点
builder.add_node(a)
builder.add_node(b)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d)

# 链接节点
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b_2")
builder.add_edge("b_2", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

# 添加持久记忆
graph = builder.compile(checkpointer=checkpointer)


# # 获取图对象的所有节点和通道
# all_node = builder.nodes    # 所有节点
# all_channels = builder.channels # 所有通道
# print(all_node)
# print(all_channels)


config={'configurable':{'thread_id':'1'}}
res = graph.invoke({"aggregate":[]},config=config)
# print(res)

# # 查看图形
# get_graph = graph.get_graph()
# res_view = get_graph.draw_ascii()
# # print(res_view)

# 查看历史所有状态
all_state= graph.get_state_history(config=config)
all_state_list = list(all_state)
for state in all_state_list:
    print(state,end="\n"+"="*30+"\n")

print("\n\n最近一次状态如下：\n")
last_state = graph.get_state(config=config)
print(last_state)