import os
import asyncio
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import  create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()

# 1、定义工具
@tool
def get_weather(city: str) -> str:
    """ 查询车票 """
    return f"{city}到上海今天有几列车。"
@tool
def transfer_money(amount: int, to_account: str) -> str:
    """ 转账工具（敏感操作）"""
    print(f"!!! 正在执行转账: {amount} -> {to_account} !!!")
    return f"成功转账 {amount} 元给 {to_account}。"

async def main():
    # 2、初始化 mcp
    client = MultiServerMCPClient({
        "12306-mcp": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "12306-mcp"
            ]
        }
    })
    # 获取 MCP 工具
    mcp_tools = await client.get_tools()

    # 3、初始化模型
    llm = init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    # 4、配置中间件,Ture暂停操作，需要用户审核
    interrupt_config = {
        "get_weather": False,
        "transfer_money": True,
    }
    hitl_middleware = HumanInTheLoopMiddleware(interrupt_on=interrupt_config)

    # 5、创建 agent
    checkpointer = InMemorySaver()
    agent = create_agent(
        model=llm,
        tools=[get_weather, transfer_money, *mcp_tools],
        middleware=[hitl_middleware],
        checkpointer=checkpointer,
    )

    # 6、测试
    # 忆测试必须使用同一个 thread_id
    config = {
        "configurable": {
            "thread_id": "test-user-001"
        }
    }
    # 测试1：MCP 查询车票
    response = await agent.ainvoke(
        {"messages": [{"role": "user","content": "帮我查询北京到上海的高铁"}]},
        config=config,
    )
    # 测试2：测试 Agent 是否记得上一轮对话
    response2 = await agent.ainvoke(
        {"messages": [{"role": "user","content": "我刚刚问的是什么问题 "}]},
        config=config,
    )
    for msg in response2["messages"]:
        print(type(msg).__name__, ":", msg.content)
    # 测试3：车票查询 get_weather
    response3 = await agent.ainvoke(
        { "messages": [ {"role": "user","content": "帮我用 get_weather 查询北京"}]},
        config=config
    )
    print(response3)
    # 测试4：转账人工审核 transfer_money
    response4 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "调用 transfer_money，amount=100，to_account=张三"}]},
        config=config,
    )
    print("中断等待人工审核：", response4)
    # 人工审核通过后，继续执行
    response5 = await agent.ainvoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
    )

    print("审核通过后的结果：", response5)


if __name__ == "__main__":
    asyncio.run(main())

