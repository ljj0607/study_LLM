import operator
from typing import TypedDict, Annotated, List
import time
import os

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langchain_openai import ChatOpenAI
from dotenv import  load_dotenv

load_dotenv()

llm_model = ChatOpenAI(
    model=os.getenv("SILICON_MODEL"),
    api_key=os.getenv("SILICON_API_KEY"),
    base_url=os.getenv("SILICON_BASE_URL"),
)


class State(TypedDict):
    """ 定义状态 """
    messages:Annotated[List[BaseMessage], operator.add]
    current_step: str

def node_input(state: State):
    """ 模拟用户输入"""
    return {
        "messages": [HumanMessage(content="请帮我写一段Python代码")],
        "current_step": "input_received"
    }

def node_processing(state: State, runtime: Runtime):
    """ 模拟中间处理过程 """
    steps = ["正在分析意图...", "正在检索知识库...", "正在构建Prompt..."]
    writer = runtime.stream_writer
    for i, step in enumerate(steps):
        time.sleep(0.5)  # 模拟耗时操作
        writer({    # 这些数据只能通过 stream_mode="custom" 接收到
            "step_index": i + 1,
            "description": step,
            "timestamp": time.time()
        })


    return {"current_step": "processing_complete"}

def node_generation(state: State, runtime: Runtime):
    """
        模拟 LLM 生成过程
        stream_mode="messages" 会自动捕获 LLM 的流式输出
    """
    # llm = runtime.context["llm"]
    # response = llm.invoke(state["messages"])

    return {
        # "messages": [response],
        "current_step": "generation_complete"
    }

builder = StateGraph(State)

builder.add_node(node_input)
builder.add_node(node_processing)
builder.add_node(node_generation)

builder.add_edge(START, "node_input")
builder.add_edge("node_input", "node_processing")
builder.add_edge("node_processing", "node_generation")
builder.add_edge("node_generation", END)

graph = builder.compile()

def run_demo():
    """ 演示不同的流式输出模式 """
    initial_state = {"messages": [], "current_step": "start"}

    print("==========(输出完整状态)==========\n")
    # print("描述: 每执行完一个节点，输出当前的完整 State")
    # for event in graph.stream(initial_state, stream_mode="values"):
    #     print(f"State:keys={list(event.keys())}, step={event.get('current_step')}

    # print("描述: 每执行完一个节点，输出该节点返回的增量数据")
    # for event in graph.stream(initial_state, stream_mode="updates"):
    #     print(f"Update: {event}")

    # print("描述: 仅输出节点内部通过 writer() 发送的数据")
    # for event in graph.stream(initial_state, stream_mode="custom"):
    #     print(f"Custom Data: {event}")

    # print("描述: 输出 LLM 生成的消息片段 (Token)")
    # for chunk, metadata in graph.stream(initial_state, stream_mode="messages", context={"llm": llm_model}):
    #     node_name = metadata.get('langgraph_node', 'unknown')
    #     print(f"[{node_name}] Token: {chunk.content!r}")

    # print("描述: 输出所有详细的执行信息，包括任务调度、输入输出等")
    # for event in graph.stream(initial_state, stream_mode="debug"):
    #     print(event)

    print("描述: 同时获取 updates 和 custom 数据")
    for mode, data in graph.stream(initial_state, stream_mode=["updates", "custom"]):
        if mode == "updates":
            print(f"[Updates] 来自节点 {list(data.keys())[0]}")
        elif mode == "custom":
            print(f"[Custom] {data['description']}")


if __name__ == "__main__":
    run_demo()