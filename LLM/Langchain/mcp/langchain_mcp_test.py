from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import  create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import AIMessage,HumanMessage,ToolMessage
from dotenv import load_dotenv
import asyncio
import os

# 1、创建 MCP
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

async def main():
    # 2、获取 MCP 工具列表
    tools = await client.get_tools()

    def handle_tool_error(error) -> str:
      return f"Tool execution failed: {str(error)}"


    for tool in tools:
      tool.handle_tool_error = handle_tool_error

    # 3、调用大模型
    load_dotenv()
    llm = llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),

    )

    # 4、创建具备工具调用能力的 Agent：llm(脑子) + tools(手脚) = agent(会干活的人)
    agent = create_agent(llm, tools)

    while True:
        user_input = input(">")
        if user_input == "exit":
            break

        res = await agent.ainvoke({
            "messages": [{"role": "user", "content": user_input}]},config={"configurable":{"thread_id":"1"}
        })

        for message in res["messages"]:
            print(message)

if __name__ == "__main__":
  asyncio.run(main())





