import os
import requests
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_unstructured import UnstructuredLoader

# 加载.env文件
load_dotenv()

# logging.basicConfig(level=logging.DEBUG)

# # 1、读取 Markdown 文档，并把文档里的每一段内容拆分成独立的文本块。
# def markdown_loader_test():
#     loader = UnstructuredLoader(
#         "./assets/sample.md",
#         encoding="utf-8",
#         chunking_strategy="by_title",
#     )
#     docs = loader.load()
#     for doc in docs:
#         print(doc.page_content, end="\n============\n")
#
# markdown_loader_test()

# # 2、读取 Word 文档（.docx），并把文档里的每一段内容拆分成独立的文本块。
# def word_loader_demo():
#     loader = UnstructuredWordDocumentLoader(
#         file_path="./assets/sample.docx",
#         mode="elements",
#     )
#     docs = loader.load()
#     for doc in docs[230:260]:  # 从文档中间选取30个文档查看结构
#         print(doc.page_content)
#         print(doc.metadata, end="\n============\n")
#
# word_loader_demo()