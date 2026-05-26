import os
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 读取环境变量
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 定义模型
llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url,
)

# 定义 Tavily 搜索工具
search = TavilySearch(
    max_results=5,
    tavily_api_key=os.getenv("TAILLY_API_KEY"),
)
tools = [search]

# 创建 agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是位助手，需要调用工具来帮助用户。"
)

# 调用 agent
# res = agent.invoke({
#     "messages": [{"role": "user", "content": "今天北京的天气怎么样？"}]
# })
# 流式返回
for chunk in agent.stream({
    "messages": [
        {"role": "system", "content": "你是位助手，需要调用工具来帮助用户。"},
        {"role": "user", "content": "今天北京的天气怎么样？"},
    ]
}):
    print(chunk, end="\n\n")

