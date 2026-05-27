### Langchain
1、langchain_openai_test：模型调用方式
2、Langchain_markdown_test：markdown 加载、读取、解析
3、milvus_test：向量数据库
4、agent_test：agent + Tavily获取实时/动态数据
5、mcp/mcp_client_stdio、mcp/mcp_server_stdio：本地开发、调试
6、mcp/mcp_http_client、mcp/mcp_server_http：生产服务、云服务
7、langchain_mcp_test：mcp + agent + langchain
8、weather_agent_test：Tavily + llm + agen + InMemorySaver，实现有记忆的 agent


### LangGraph
1、start_type_dict：TypedDict类型
2、start_base_model：BaseModel
3、start_reducer：reducer 累计，自定义reducer
4、node_history: 获取历史记录
5、node_input： Runtime 节点输入
6、node_output：节点输出
7、node_cache：节点缓存
8、node_sqlite：长期记忆
9、node_retry：重试策略
10、node_stream：内外数据传递
11、node_edge：动态决定下一步流转到哪个节点（边）
12、node_loop：环链接
13、node_transfer：人工审核（节点暂停、节点续接)
