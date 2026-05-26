import asyncio
import sys
from pathlib import Path
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def stdio_run():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["./mcp_server_stdio.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化链接
            await session.initialize()

            # 获取可用工具
            tools = await session.list_tools()

            # 调用工具
            call_res = await session.call_tool("add", {"a": 1, "b": 2})

            # 获取可用资源
            resources = await session.list_resources()

            # 调用资源
            read_res = await session.read_resource("greeting://default")

            # 获取可用提示
            prompts = await session.list_prompts()

            # 调用提示
            get_res = await session.get_prompt("greet_user", {"name": "Jack"})
            print(get_res)

asyncio.run(stdio_run())