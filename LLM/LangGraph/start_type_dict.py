from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph

class MyState(TypedDict):
    query:str
    reg_search_result:str
    web_search_result:str
    final_result:str

# 初始化 LangGraph
graph = StateGraph(MyState)

def rag_search_node(state: MyState):
    query = state["query"]
    reg_search_result = f"关于{query}的reg_search_result"
    return {"reg_search_result": reg_search_result}

def web_search_node(state: MyState):
    query = state["query"]
    web_search_result = f"关于{query}的web_search_result"
    return {"web_search_result": web_search_result}

def final_result_node(state: MyState):
    reg_search_result = state["reg_search_result"]
    web_search_result = state["web_search_result"]
    final_result = f"LLM基于{reg_search_result}和{web_search_result}的最终回复"
    return {"final_result": final_result}

# 新增节点
graph.add_node(rag_search_node)
graph.add_node(web_search_node)
graph.add_node(final_result_node)

# 链接节点
graph.add_edge(START, "rag_search_node")
graph.add_edge(START, "web_search_node")
graph.add_edge("rag_search_node", "final_result_node")
graph.add_edge("web_search_node", "final_result_node")
graph.add_edge("final_result_node", END)

# 编译
compiled_graph = graph.compile()
response= compiled_graph.invoke({"query":"如何使用LangGraph"})
print(response)

# 查看图的结构
graph_structure = compiled_graph.get_graph()
res = graph_structure.draw_ascii()
print(res)