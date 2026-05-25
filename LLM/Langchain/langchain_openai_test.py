"""  模型调用方式 """

import os
import time
import base64
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import (HumanMessage,SystemMessage,AIMessage)

# # langchain 底层使用格式
# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     base_url=os.getenv("OPENAI_BASE_URL"),
# )
# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[{"role": "user", "content": "将'你好'翻译成意大利语"}],
# )
# print(completion.choices[0].message.content)

# 加载.env文件
load_dotenv()

# 读取环境变量
api_key = os.getenv("SILICON_API_KEY")
base_url = os.getenv("SILICON_BASE_URL")

# # 1、常规操作
# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     api_key=os.getenv("OPENAI_API_KEY"),
#     base_url=os.getenv("OPENAI_BASE_URL"),
#     temperature=0.7,            # 随机性，0=确定性，1=有创意（默认因模型而异）
#     max_tokens=1000,            # 最大输出长度
#     timeout=60,                 # 超时时间（秒）
#     max_retries=2,              # 失败重试次数
#
# )
# response = llm.invoke("请用一句话介绍 python")
# print(response)

# # 2、动态切换模型
# llm_openai = init_chat_model("deepseek-chat", model_provider="deepseek",api_key=api_key,base_url=base_url)
# for name, llm in [('Deepseek', llm_openai)]:
#     response = llm.invoke("用一句话介绍自己")
#     print(response)

# # 3、 构建完整的历史对话
# llm = ChatOpenAI(
#      model="deepseek-chat",
#      api_key=api_key,
#      base_url=base_url,
# )
# conversation = [
#     SystemMessage(content="你是一个有帮助的AI助手"),  # 设定 ai 的行为/角色
#     HumanMessage(content="你好，我叫hzk"),   # 用户的输入
#     AIMessage(content="你好！hzk,有什么我可以帮助你的吗？"),   # ai 回复
#     HumanMessage(content="我叫什么名字？"),    # 工具执行返回结果
# ]
# response = llm.invoke(conversation)
# print(response)

# # 4、异步
# llm = ChatOpenAI(
#      model="deepseek-ai/DeepSeek-V4-Flash",
#      api_key=api_key,
#      base_url=base_url,
# )
# async def call_llm_async():
#     response = await llm.ainvoke("什么是 langchain")
#     print(response)
# print(asyncio.run(call_llm_async()))

# # 5、同步 invoke（串行）
# prompts = ["用一句话介绍一下北京", "用一句话介绍一下上海", "用一句话介绍一下广州", "用一句话介绍一下深圳", "用一句话介绍一下杭州"]
# llm = ChatOpenAI(
#      model="deepseek-chat",
#      api_key=api_key,
#      base_url=base_url,
# )
# def test_async_ainvoke():
#     start_time = time.time()
#
#     for i, prompt in enumerate(prompts):
#         print(i, prompt)
#         llm.invoke(prompts)
#     print(f"总耗时：{time.time() - start_time}秒")
# test_async_ainvoke()

# # 6、异步 ainvoke（并行）
# prompts = ["用一句话介绍一下北京", "用一句话介绍一下上海", "用一句话介绍一下广州", "用一句话介绍一下深圳", "用一句话介绍一下杭州"]
# llm = ChatOpenAI(
#      model="deepseek-ai/DeepSeek-V4-Flash",
#      api_key=api_key,
#      base_url=base_url,
# )
# async def test_async_ainvoke():
#     start_time = time.time()
#     tasks = [llm.ainvoke(prompt) for prompt in prompts]
#     results = await asyncio.gather(*tasks)
#
#     for r in results:
#         print(f"回答{r.content[:20]}...")
#     print(f"总耗时{time.time() - start_time}")
# asyncio.run(test_async_ainvoke())

# # 7、流式调用 - stream
# def streamumg_example():
#     llm = ChatOpenAI(
#         model="deepseek-ai/DeepSeek-V4-Flash",
#         api_key=api_key,
#         base_url=base_url,
#     )
#     full_message = None
#     for chunk in llm.stream("请写一首春天的诗"):
#         full_message = chunk if full_message is None else full_message + chunk
#     print(full_message)
# streamumg_example()

# # 8、批次调用 - batch（并行处理）
# def batch_example():
#     llm = ChatOpenAI(
#         model="deepseek-ai/DeepSeek-V4-Flash",
#         api_key=api_key,
#         base_url=base_url,
#     )
#     questions = ["什么是Python？", "什么是JavaScript？", "什么是Go语言？"]
#     responses = llm.batch(questions)
#     for q, r in zip(questions, responses):
#         print(f"Q: {q}")
#         print(f"A: {r.content}\n")
# batch_example()

# # 9、异步批次
# async def batch_async():
#     llm = ChatOpenAI(
#         model="deepseek-ai/DeepSeek-V4-Flash",
#         api_key=api_key,
#         base_url=base_url,
#     )
#     questions = ["什么是Python？", "什么是JavaScript？", "什么是Go语言？"]
#     response = await llm.abatch(questions)
#     for q, r in zip(questions, response):
#         print(f"Q: {q}\nA: {r.content}\n")
# asyncio.run(batch_async())

# 10、分析图片
llm = ChatOpenAI(
    model="Pro/moonshotai/Kimi-K2.6",
    api_key=api_key,
    base_url=base_url,
)
with open("IMG_2851.JPG", "rb") as f:
    image_data = f.read()

message = HumanMessage(content=[
    {"type": "text", "text": "描述这张图片"},
    {   "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"}
    }
])
response = llm.invoke([message])
print(response.content)





