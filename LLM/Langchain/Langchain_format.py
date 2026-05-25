import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 加载.env文件
load_dotenv()

# 读取环境变量
api_key = os.getenv("SILICON_API_KEY")
base_url = os.getenv("SILICON_BASE_URL")

# 调用模型
llm = ChatOpenAI(model="deepseek-ai/DeepSeek-V4-Flash",api_key=api_key, base_url=base_url)
llm_openai = init_chat_model("deepseek-chat", model_provider="deepseek",api_key=os.getenv("DEEPSEEK_API_KEY"),base_url=os.getenv("DEEPSEEK_BASE_URL"))

# # 1、处理大模型的输入格式
# def langchain_format():
#     class FormatModal(BaseModel):
#         name: list[str] = Field(description="名称")
#         description: list[str]  = Field(description="描述")
#
#     # 获取使用指定的结构获取结果的大模型对象
#     llm_format = llm.with_structured_output(FormatModal)
#     response = llm_format.invoke([
#         ("user", "总结一年中比较重要的节日")
#     ])
#     print(response)
# langchain_format()

# # 2、提示模板功能
# def langchain_prompt():
#     prompt_template = ChatPromptTemplate.from_messages(
#         messages=[
#             ("system", "你是一个专业的评论员"),
#             ("user", "请评论[product]的优缺点，包括[aspect]和[aspect2]"),
#         ]
#     )
#     prompt = prompt_template.invoke({
#         "product": "联想",
#         "aspect": "性能",
#         "aspect2": "性价比"
#     })
#     print(prompt)
# langchain_prompt()

# # 3、按顺序“链接”多个可运行对象，其中一个对象的输出作为下一个对象的输入
# prompt_template = PromptTemplate(
#     template="讲一个关于{topic}的笑话",
#     input_variables=["topic"],
# )
# parser = StrOutputParser()  # 创建解释器对象
# chain = prompt_template | llm_openai | parser
# resp = chain.invoke({"topic":"人工智能"})
# print(resp)

# 4、同时运行多个对象，并为每个对象提供相同的输入
english_chain = (PromptTemplate.from_template("把这个句子{topic}翻译成英文")) | llm_openai | StrOutputParser()
korean_chain = (PromptTemplate.from_template("把这个句子{topic}翻译成韩语")) | llm_openai | StrOutputParser()
map_chain = RunnableParallel(english=english_chain, korean=korean_chain)
resp = map_chain.invoke({"topic":"好好学习，天天向上"})
print(resp)
















