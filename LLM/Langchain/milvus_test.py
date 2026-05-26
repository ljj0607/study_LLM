import numpy as np
import os
from typing import Dict, List
from pymilvus import MilvusClient, DataType, AnnSearchRequest, RRFRanker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from FlagEmbedding import BGEM3FlagModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

COLLECTION_NAME = "demo_collection"

# 链接 default 数据库
def get_milvus_client():
    client = MilvusClient(uri="http://47.116.51.88:19530/default")
    return client

# 添加字段
def build_schema():
    return (
        MilvusClient.create_schema(auto_id=True)
        # is_primary 设为主键
        .add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        # DataType.FLOAT_VECTOR 稠密向量
        .add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        .add_field(field_name="text", datatype=DataType.VARCHAR, max_length=1500)
        .add_field(field_name="metadata", datatype=DataType.JSON)
        # SPARSE_FLOAT_VECTOR 稀疏向量
        .add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
    )

# 构建Milvus向量索引
def build_index():
    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="L2",
        params={
            "M": 16,
            "efConstruction": 200  # 显式指定有效值
        }
    )
    index_params.add_index(field_name="sparse_vector", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
    return index_params

# 建表
def create_collection():
    client = get_milvus_client()
    client.drop_collection(collection_name=COLLECTION_NAME)
    if not client.has_collection(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            schema=build_schema(),
            index_params=build_index(),
        )

# 加载 BGE-M3 嵌入模型
def get_bge_m3_model():
    return BGEM3FlagModel("./assets/models/bge-m3")

# 插入数据
def insert_data(client: MilvusClient, collection_name: str):
    # 1、加载文档
    loader = UnstructuredLoader("./assets/sample.docx", mode="single")
    doc_list = loader.load()

    # 2、切分文件
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。"]
    )
    splitted_doc_list = text_splitter.split_documents(doc_list)

    # 3、构建向量：稠密向量、稀疏向量
    model = get_bge_m3_model()
    # return_dense 返回稠密向量，return_sparse 返回稀疏向量
    all_vectors = model.encode([doc.page_content for doc in splitted_doc_list], return_dense=True, return_sparse=True)
    dense_vectors = all_vectors["dense_vecs"]
    sparse_vectors = all_vectors['lexical_weights']
    # print(dense_vectors, sparse_vectors)
    # 转换数据类型
    dense_vectors = dense_vectors.astype(np.float32)

    # 4、准备数据，组装成 list[Dict]
    insert_data_list = []
    for doc, dense_vec, sparse_vec in zip(splitted_doc_list, dense_vectors, sparse_vectors):
        insert_data_list.append({
            "vector": dense_vec.tolist(),
            "sparse_vector": sparse_vec,
            "metadata": doc.metadata,
            "text": doc.page_content,

        })

    # 5、调用 client.insert()方法，插入数据
    client.insert(collection_name=collection_name, data=insert_data_list)

# 删除数据
def delete_data(client: MilvusClient, collection_name: str):
    res = client.delete(
        collection_name=collection_name,
        # 删除 id 在指定的数据,
        filter="id in [466534145003136499, 466534145003136500]"
    )

def print_hits(title:str, hits: List[Dict]):
    print(title)
    for i, hit in enumerate(hits, start=1):
        entity = hit.get("entity", {})
        print({
            "rank": i,
            "id": entity.get("id"),
            "distance": hit.get("distance"),
            "text": entity.get("text"),
            "metadata": entity.get("metadata"),
        })

# 返回 -> 稠密向量、稀疏向量
def encode_query(model, query: str):
    result = model.encode_queries([query],return_dense=True,return_sparse=True)
    dense_vec = result["dense_vecs"][0].astype(np.float32)
    sparse_vec = result["lexical_weights"][0]
    return dense_vec, sparse_vec

# 稠密向量检索（sparse_vector）
def dense_vector_search_example(client: MilvusClient, query: str, limit: int = 5):
    model = get_bge_m3_model()
    dense_vec, _ = encode_query(model, query)

    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[dense_vec],
        anns_field="vector",
        limit=limit,
        search_params={"metric_type": "L2"},
        output_fields=["id", "text", "metadata"],
    )
    print_hits("稠密向量检索（vector）", results[0])
    return results

# 稀疏向量检索（vector）
def sparse_vector_search_example(client: MilvusClient, query: str, limit: int = 5):
    model = get_bge_m3_model()
    _, sparse_vec = encode_query(model, query)
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[sparse_vec],
        anns_field="sparse_vector",
        limit=limit,
        search_params={"metric_type": "IP"},
        output_fields=["id", "text", "metadata"],
    )
    print_hits("稀疏向量检索（sparse_vector）", results[0])
    return results

# 混合向量检索（RRF 融合稠密+稀疏）
def hybrid_vector_search_example_rrf(client: MilvusClient, query: str, limit: int = 5):
    model = get_bge_m3_model()
    dense_vec, sparse_vec = encode_query(model, query)
    dense_req = AnnSearchRequest(
        data=[dense_vec],
        anns_field="vector",
        param={"metric_type": "L2"},
        limit=limit,
    )
    sparse_req = AnnSearchRequest(
        data=[sparse_vec],
        anns_field="sparse_vector",
        param={"metric_type": "IP"},
        limit=limit,
    )
    results = client.hybrid_search(
        collection_name=COLLECTION_NAME,
        reqs=[dense_req, sparse_req],
        ranker=RRFRanker(k=60),
        limit=limit,
        output_fields=["id", "text", "metadata"],
    )
    # print_hits("混合向量检索（RRF 融合稠密+稀疏）", results[0])
    return results

# 标量查询示例：根据关键词模糊匹配文本内容
def scalar_query_examples(client: MilvusClient, like_keyword:str = "法人", limit: int = 5):
    # 对text字段进行检索
    try:
        like_res = client.query(
            collection_name=COLLECTION_NAME,
            filter=f"text like '%{like_keyword}%'",
            out_fields=["id", "text"],
            limit=limit,
        )
        for row in like_res:
            print({"id": row.get("id"), "text": row.get("text")})
    except Exception as error:
        print("VARCHAR like 过滤失败：", error)

    try:
        json_res = client.query(
            collection_name=COLLECTION_NAME,
            filter='metadata["source"] like "%sample%"',
            output_fields=["id", "metadata"],
            limit=limit,
        )
        for row in json_res:
            print({"id": row.get("id"), "metadata": row.get("metadata")})

    except Exception as error:
        print("JSON 过滤失败（metadata 结构不匹配或不支持该表达式）：", error)

# 生成
def rag_demo(client: MilvusClient, query: str):
    # 加载.env文件
    load_dotenv()

    # 读取环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    # 加载模型
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, base_url=base_url)
    retrieval_res = hybrid_vector_search_example_rrf(client, query, 10)

    print(retrieval_res)

    # 构建上下文
    results_list = retrieval_res[0]
    context = "\n".join([data["entity"]["text"] for data in results_list])

    print(context)
    message_list = [{
        "role": "system",
        "content": "你是一个专业的法律问答机器人，请根据上下文回答问题，当上下文无法回答问题时，请回答“根据上下文无法回答该问题”"},
        {"role": "user", "content": f"根据以下上下文回答问题：{context}\n问题：{query}"
    }]

    # 生成文本
    res = llm.invoke(message_list)
    print(res)

# create_collection()
# insert_data(get_milvus_client(), COLLECTION_NAME)
# delete_data(get_milvus_client(), COLLECTION_NAME)
# dense_vector_search_example(get_milvus_client(), "民法典财产权")
# sparse_vector_search_example(get_milvus_client(), "合同")
# hybrid_vector_search_example_rrf(get_milvus_client(), "合同")
# scalar_query_examples(get_milvus_client(), "合同")
# scalar_query_examples(get_milvus_client(), "自然人")
rag_demo(get_milvus_client(), "民法典中自然人的民事权利能力从什么时候开始？")
