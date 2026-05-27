import time
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

"""
    演示 LangGraph 节点缓存 CachePolicy 的使用。
    
    功能：
    1. expensive_node 模拟一个耗时节点，执行时会 sleep 5 秒。
    2. 给 expensive_node 配置 cache_policy=CachePolicy(ttl=10)，表示节点结果缓存 10 秒。
    3. graph.compile(cache=InMemoryCache()) 开启节点缓存能力。
    4. 两次 invoke 输入相同的 x=5，即使 thread_id 不同，第二次也会命中节点缓存，避免重复执行耗时节点。
    5. checkpointer=InMemorySaver() 用于保存不同 thread_id 的执行状态，方便后续状态恢复。
"""

class State(TypedDict):
    x: int
    result: int


# 1、定义节点：模拟一些有耗时计算的节点
def expensive_node(state: State) -> dict[str, int]:
    print("进入节点，开始执行...")
    time.sleep(5)
    return {"result": state["x"] * 2}


checkpointer = InMemorySaver()
builder = StateGraph(State)
# 2、为节点配置缓存策略，这里设置为10秒缓存，缓存键的配置同样使用默认的方式，可以在CachePolicy当中传入key_func配置不同的缓存键生成策略
builder.add_node("expensive_node", expensive_node, cache_policy=CachePolicy(ttl=10))
builder.add_edge(START, "expensive_node")

# 3、编译图，并增加“缓存能力”和“状态持久化能力”。
graph = builder.compile(
    cache=InMemoryCache(),  # 节点缓存
    checkpointer=checkpointer   # 状态记忆/恢复
)
start = time.time()
print("---1",graph.invoke({"x": 5},config={"configurable":{"thread_id":"1"}}))
print("耗时:", time.time()-start)
start = time.time()
print("---2",graph.invoke({"x": 5},config={"configurable":{"thread_id":"2"}}))
print("耗时:", time.time()-start)




