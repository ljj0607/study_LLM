import os
import datetime
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_tavily import  TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

# 加载 .env文件
load_dotenv()

# 读取环境变量
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
api_tavily = os.getenv("TAVILY_API_KEY")

# 1、定义 Tavily 搜索工具
search = TavilySearch(max_results=5, tavily_api_key=api_tavily)
tools = [search]

# 2、创建大模型
llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    api_key=api_key,
    base_url=base_url,
)

# 3、给 agent 添加记忆
checkpointer = InMemorySaver()

# 4、创建 agent
agent = create_agent(model=llm, tools=tools, checkpointer=checkpointer)

if __name__ == "__main__":
    for chunk in agent.stream(
        input={
            "messages":[
                {"role": "system", "content": f"当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
                {"role": "user", "content": "今天北京天气怎么样？"},
            ],
        },
        # 关键点3：为每个调用指定一个唯一的thread_id
        config={"configurable": {"thread_id": "abc123"}},
    ):
        print(chunk, end="\n\n")

    print("=== 第二次调用 ===")
    for chunk in agent.stream(
         input={
             "messages": [{"role": "user", "content": "我刚才问你什么了"}]
        },
        # 关键点4：在多次调用中使用相同的thread_id，模型会记住之前的对话
        config = {"configurable": {"thread_id": "abc123"}},
    ):
        print(chunk, end="\n\n")



