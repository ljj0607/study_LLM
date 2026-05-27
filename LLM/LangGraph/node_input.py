import time
from typing import List, TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime

"""
    LangGraph Runtime 依赖注入示例

    功能：
    1. 创建客服状态图（Customer Support Graph）
    2. 使用 Runtime.context 注入外部依赖：
       - LLM（模拟大模型）
       - Database（模拟数据库）
    3. 使用 RunnableConfig 传递运行配置：
       - user_id
       - thread_id 等
    4. 在节点中根据用户信息动态处理业务逻辑
    5. 使用 stream_writer 输出实时状态
    6. 返回最终处理结果
"""


class MockLLM:
    def invoke(self, prompt: str):
        return f"AI Generated: Answer for '{prompt}'"

class MockDatabase:
    def get_user_info(self, user_id: str):
        return {"id": user_id, "role": "vip" if "vip" in user_id else "standard"}

class CustomerSupportState(TypedDict):
    """ 类型设置 """
    query: str
    response: str
    log: List[str]

def node_customer_service(state: CustomerSupportState, config: RunnableConfig, runtime: Runtime) -> dict:
    """ 客服节点 """

    # 1、从runtime当中获取context对象
    user_query = state["query"]
    llm = runtime.context["llm"]
    db = runtime.context["db"]
    configurable = config.get("configurable")
    user_id = configurable.get("user_id", "guest")
    print(f"\n[Node] 开始处理，User ID: {user_id}")

    # 2、验证依赖是否存在
    if not llm or not db:
        return {"response": "System Error: Dependencies not injected!", "log": ["Error"]}

    # 3、使用db对象查看用户角色
    user_info = db.get_user_info(user_id)
    user_tier = user_info.get("role")
    print(f"[Node] 从 DB 获取用户角色: {user_tier}")

    # 4、使用 runtime.writer 向图外输出自定义数据 ---
    writer = runtime.stream_writer
    writer({"status": "thinking", "message": f"正在调用 LLM 为 {user_tier} 用户生成回复..."})
    time.sleep(0.5)

    # 5、根据用户角色构建不同的 Prompt，并模拟 LLM 调用
    prompt = f"User({user_tier}) asks: {user_query}"
    llm_response = llm.invoke(prompt)

    return {"response": llm_response, "log": [f"Processed by {llm.__class__.__name__}"]}

def run_demo():
    builder = StateGraph(CustomerSupportState)
    builder.add_node(node_customer_service)
    builder.add_edge(START,"node_customer_service")
    builder.add_edge("node_customer_service",END)
    graph = builder.compile()

    # 初始化外部依赖
    my_llm = MockLLM()
    my_db = MockDatabase()

    initial_state = {"query": "如何升级会员？"}
    config = {"configurable": {"user_id": "vip_user_999"}}
    context = {"llm": my_llm, "db": my_db}

    result = graph.invoke(initial_state, config=config, context=context)
    print(result)



if __name__ == "__main__":
    run_demo()



