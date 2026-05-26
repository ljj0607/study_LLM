import asyncio
from mcp import  ClientSession
from mcp.client.streamable_http import streamable_http_client

async def streamablehttp_run():
    url = "http://127.0.0.1:8000/mcp"

    async with streamable_http_client(url=url) as (read, writer, _):
        async with ClientSession(read=read, write=writer) as session:

            # 初始化链接
            await session.initialize()

            # 获取可用工具
            await session.list_tools()

            # 调用工具
            call_res = await session.call_tool("add", {"a": 1, "b": 2})

            # 获取可用资源
            read_res = await session.read_resource("greeting://default")

            # 获取可用提示
            prompts = await session.list_prompts()

            # 调用提示
            get_res = await session.get_prompt("greet_user", {"name": "Jack"})



asyncio.run(streamablehttp_run())