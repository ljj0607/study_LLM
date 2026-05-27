import sqlite3
from typing import TypedDict
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

"""
    LangGraph 并行节点状态合并示例
    
    功能说明：
    1. 接收用户问题(query)
    2. 并行执行网络搜索(query_web)
    3. 并行执行文件搜索(query_file)
    4. 汇总多个节点结果(answer)
    5. 输出最终 LLM 回复
"""

# 创建 SQLite 数据库连接（不存在会自动创建），允许多线程共享连接
connection = sqlite3.connect("./langgraph_sqlite.db", check_same_thread=False)

# 创建 SQLite checkpoint saver
memory = SqliteSaver(connection)

class MyState(TypedDict):
    """ 类型定义 """
    query: str
    web_result: str
    file_result: str
    final_answer: str

def query_web(state: MyState):
    """ 网络搜索， 返回网络搜索 """
    query = state['query']
    return {"web_result": f'{query}的网络搜索结果'}

def query_file(state: MyState):
    """ 做文件搜索，返回搜索结果 """
    query = state['query']
    return {"file_result": f'{query}的文件搜索结果'}

def answer(state: MyState):
    """ 返回最终的答案 """
    web_result = state['web_result']
    file_result = state['file_result']
    return {"final_answer": f'LLM基于{web_result}，{file_result} 的最终结果'}

# 创建构建图
builder = StateGraph(MyState)

# 新增节点
builder.add_node(query_web)
builder.add_node(query_file)
builder.add_node(answer)

#链接节点
builder.add_edge(START, "query_web")
builder.add_edge(START, "query_file")
builder.add_edge("query_web", "answer")
builder.add_edge("query_file", "answer")
builder.add_edge("answer", END)

# 持久化
config={'configurable':{'thread_id':'1'}}

# 构建
graph = builder.compile(checkpointer=memory)
res = graph.invoke({"query":"什么是Langgraph"},config=config)
print(res)

# 查看图形
get_graph = graph.get_graph()
res_view = get_graph.draw_ascii()
print(res_view)