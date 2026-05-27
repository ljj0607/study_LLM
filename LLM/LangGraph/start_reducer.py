from typing import List, TypedDict, Annotated
from langgraph.graph import  StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage,HumanMessage,AIMessage,BaseMessage
from torch._functorch._aot_autograd import graph_compile


# # 1、默认 reducer（覆盖更新）
# class DefaultReducerState(TypedDict):
#     foo: int
#     bar: List[str]
#
# def node_one1(state: DefaultReducerState) -> dict:
#     return { "foo":2}
#
# def node_one2(state: DefaultReducerState) -> dict:
#     return { "bar":["hello"]}
#
# def run_main():
#     # 初始化 LangGraph
#     graph = StateGraph(DefaultReducerState)
#
#     # 新建 node
#     graph.add_node(node_one1)
#     graph.add_node(node_one2)
#
#     # 链接
#     graph.add_edge(START, "node_one1")
#     graph.add_edge("node_one1", "node_one2")
#     graph.add_edge("node_one2", END)
#
#     res_graph = graph.compile()
#     result = res_graph.invoke({"foo": 1, "bar": ["hi"]})
#     print(result)
#
# if __name__ == "__main__":
#     run_main()

# 2、自定义 reducer
def add_messages(message_list_left: list, message_list_right: list):
    print("=="*20)
    return message_list_left + message_list_right

class MyAgent(TypedDict):
    # # 在初始使用自定义的reducer
    # messages: Annotated[List[BaseMessage], add_messages]
    messages: Annotated[List[BaseMessage], add_messages]



def tool_node(state:MyAgent):
    return {"messages": [ToolMessage(content="来自tool_node的内容", tool_call_id="xxx")]}

def llm_node(state:MyAgent):
    return {"messages": [AIMessage(content="来自llm_node的内容")]}

graph = StateGraph(MyAgent)

graph.add_node(tool_node)
graph.add_node(llm_node)

graph.add_edge(START, "tool_node")
graph.add_edge("tool_node", "llm_node")
graph.add_edge("llm_node", END)

graph_compile = graph.compile()
res = graph_compile.invoke({"messages":[HumanMessage(content="你好")]})
print(res)



