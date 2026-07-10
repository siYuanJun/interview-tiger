# 机械臂提取报告 — RAG 3.0 升级验证

生成时间: 2026-07-10

## 提取摘要

| 项目 | 值 |
|------|-----|
| 框架 | Python FastAPI |
| 路由注册 | `main.py:82-90` |
| Base URL (Docker host) | `http://localhost:8001` |
| Base URL (Docker internal) | `http://localhost:8000` |

## 接口 1: POST /api/question

| 提取项 | 来源 | 值 |
|--------|------|-----|
| HTTP 方法 | `question.py:62 @router.post` | POST |
| URL 路径 | `main.py:88 prefix="/api"` + `question.py:62 "/question"` | `/api/question` |
| question | `question.py:17` | str, min_length=1, max_length=2000, **必填** |
| ark_api_key | `question.py:18` | str, 可选, default="" |
| model_id | `question.py:19` | str, 可选, default=ARK_MODEL |
| kb_id | `question.py:20` | str, 可选, default="" |
| kb_api_key | `question.py:21` | str, 可选, default="" |
| kb_provider | `question.py:22` | str, 可选, default="" |
| stream | `question.py:23` | bool, 可选, default=True |
| session_id | `question.py:24` | str, 可选, default="" (RAG3 新增) |
| 返回结构 | `question.py:107-116` | `{code, message, data: {answer, knowledge_used, web_search_used, source_chunks}}` |
| 知识库调用 | `question.py:43-59 fetch_knowledge_sync()` | 根据 kb_provider 路由到 local/volcengine provider |
| 降级策略 | `question.py:87-89` | 知识库无结果→开启联网搜索 |

## 接口 2: POST /api/question/stream

| 提取项 | 来源 | 值 |
|--------|------|-----|
| HTTP 方法 | `question.py:119` | POST |
| URL 路径 | `main.py:88` + `question.py:119` | `/api/question/stream` |
| 请求体 | `question.py:120` | 同 QuestionRequest |
| 返回类型 | `question.py:168-176` | `text/event-stream` SSE |
| SSE 事件类型 | `question.py:151-166` | status / chunk / done / error |

## RAG 3.0 管线（local_knowledge.py:157-223）

| 步骤 | 来源行 | 模块 | 说明 |
|------|--------|------|------|
| 1. 跟进检测 | `167-171` | SessionMemory | is_follow_up() 检测→命中则返回缓存 |
| 2. 查询扩展 | `174-178` | QueryRewriter | expand() 最多3个变体 |
| 3. 混合检索 | `181-200` | HybridRetriever | BM25+Dense+RRF，降级纯向量 |
| 4. 去重 | `193-197` | - | seen set 按 content 去重 |
| 5. 内容校验 | `206-210` | ContentValidator | LLM 批量判断 YES/NO，超时兜底 |
| 6. 拼接 | `213` | - | '\n'.join(validated[:top_k]) |
| 7. 缓存 | `216-217` | SessionMemory | set() 缓存结果供跟进命中 |

## RAG 3.0 配置（config.py:38-46）

| 配置项 | 环境变量 | 默认值 |
|--------|----------|--------|
| BM25_WEIGHT | BM25_WEIGHT | 0.3 |
| HYBRID_ENABLED | HYBRID_ENABLED | true |
| QUERY_EXPAND_ENABLED | QUERY_EXPAND_ENABLED | true |
| VALIDATOR_ENABLED | VALIDATOR_ENABLED | true |
| VALIDATOR_TIMEOUT | VALIDATOR_TIMEOUT | 3.0 |
| SESSION_MEMORY_ENABLED | SESSION_MEMORY_ENABLED | true |
| SESSION_MEMORY_TTL | SESSION_MEMORY_TTL | 1800 |
| SESSION_MEMORY_MAX | SESSION_MEMORY_MAX | 50 |

## 新增文件

| 文件 | 模块 | 行数 |
|------|------|------|
| `backend/app/services/hybrid_retriever.py` | BM25+Dense RRF 混合检索 | ~120 |
| `backend/app/services/query_rewriter.py` | 同义词查询扩展 | ~80 |
| `backend/app/services/memory.py` | 会话内存缓存 | ~100 |
| `backend/app/services/validator.py` | LLM 内容校验 | ~90 |
