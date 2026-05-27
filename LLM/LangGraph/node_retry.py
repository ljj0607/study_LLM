from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy

"""
    重试策略
    1. LangGraph 节点如何配置 RetryPolicy 重试策略
    2. 节点发生异常后，LangGraph 如何自动重试
    3. max_attempts 参数的作用
    4. 不同异常在重试后的最终表现
    5. graph.invoke() 如何捕获最终失败异常
"""

class State(TypedDict):
    """ 定义状态 """
    result: str

attempt_counter = 0

def unstable_api_call(state:State):
    """ 模拟 一个不稳定的 api 调用"""

    global attempt_counter
    attempt_counter += 1
    print(f"尝试调用API，这是第 {attempt_counter} 次尝试")

    # 模拟前几次尝试失败，最后一次成功
    if attempt_counter < 3:
        raise Exception(f"模拟API调用失败 (尝试 {attempt_counter})")
    else:
        return {"result": f"API调用成功，经过 {attempt_counter} 次尝试"}




def value_error_call(state:State):
    """" 模拟抛出 ValueError 的节点"""
    print(state)
    raise ValueError("模拟 ValueError 异常")

def run_demo():
    global attempt_counter
    attempt_counter = 0

    # 构建视图
    builder = StateGraph(State)

    # 添加节点，使用默认重试策略
    builder.add_node(
        "unstable_api_call",
        unstable_api_call,
        retry_policy=RetryPolicy(max_attempts=5)  # 允许最多5次尝试
    )
    builder.add_node(
        "value_error_call",
        value_error_call,
        retry_policy=RetryPolicy(max_attempts=3)
    )

    # 链接节点
    builder.add_edge(START, "unstable_api_call")
    builder.add_edge("unstable_api_call", "value_error_call")
    builder.add_edge("value_error_call", END)

    # 构建
    graph = builder.compile()

    print("====================测试默认重试策略:")
    try:
        result = graph.invoke({"result": ""})
        print(result)
    except Exception as e:
        print(f"最终失败{type(e).__name__}:{e}\n")





if __name__ == "__main__":
    run_demo()