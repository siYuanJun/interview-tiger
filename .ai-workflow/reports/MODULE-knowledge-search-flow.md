# 知识库检索模块 - 流程文档

## 模块概述
- **功能定位**: 实现火山引擎知识库的检索服务，支持SignerV4签名认证，从知识库中检索与面试问题相关的用户简历/项目经历信息
- **核心价值**: 为大模型提供个性化的上下文信息，让回答更贴合用户的真实经历

## 核心流程

### 知识库检索主流程

```mermaid
sequenceDiagram
    participant 前端
    participant 后端路由
    participant 知识库服务
    participant 火山引擎RAG API

    前端->>后端路由: POST /api/search (query, kb_id, kb_api_key)
    后端路由->>知识库服务: search_knowledge(query, kb_id, kb_api_key)
    知识库服务->>知识库服务: 拆解AK:SK格式API Key
    知识库服务->>知识库服务: 构建SignerV4签名
    知识库服务->>火山引擎RAG API: POST /api/v1/retrieval/search
    火山引擎RAG API-->>知识库服务: 返回检索结果JSON
    知识库服务->>知识库服务: get_relevant_knowledge()过滤低相关性结果
    知识库服务->>知识库服务: 优先使用rerank_score排序
    知识库服务->>知识库服务: 过滤score<0.3的低相关结果
    知识库服务->>知识库服务: 最多取3条，拼接为上下文文本
    alt 检索成功
        知识库服务-->>后端路由: 返回上下文文本
        后端路由-->>前端: {code:0, message:"success", data:{context}}
    else 检索失败(网络错误/认证失败/无结果)
        知识库服务-->>后端路由: 返回空字符串或错误信息
        后端路由-->>前端: {code:0, message:"success", data:{context:""}}
    end
```

### 结果过滤逻辑

```mermaid
flowchart TD
    A[获取检索原始结果] --> B{result_list存在?}
    B -->|否| C[返回空字符串]
    B -->|是| D[遍历result_list]
    D --> E{rerank_score存在?}
    E -->|是| F[使用rerank_score排序]
    E -->|否| G[使用默认score排序]
    F --> H[过滤score<0.3的结果]
    G --> H
    H --> I{结果数>3?}
    I -->|是| J[取前3条]
    I -->|否| K[保留全部]
    J --> L[用换行符拼接内容]
    K --> L
    L --> M[返回上下文文本]
```

## 涉及文件清单
| 文件 | 作用 | 层级 |
|-----|------|------|
| backend/app/services/knowledge.py | 知识库检索核心服务 | 服务 |
| backend/app/routes/search.py | 知识库检索API路由 | 路由 |
| backend/app/routes/question.py | 问题处理路由（调用知识库） | 路由 |
| backend/app/services/prompt.py | Prompt拼接（使用知识库结果） | 服务 |
| backend/config.py | 环境变量配置（默认KB_API_KEY） | 配置 |

## 关键逻辑通俗解释

> 用大白话解释核心逻辑，让非技术人员也能理解。

知识库检索模块就像是面试虎的记忆库。它的工作流程：

1. **接收问题**: 后端收到面试问题后，需要从知识库中查找相关信息
2. **准备钥匙**: 把用户配置的API Key拆成Access Key和Secret Key，就像准备开锁的钥匙
3. **签名认证**: 生成SignerV4签名，就像在请求上盖个章证明身份
4. **检索记忆**: 向火山引擎知识库发送请求，查找与问题相关的用户简历、项目经历等信息
5. **筛选重要信息**: 
   - 只保留相关性高的内容（分数>0.3）
   - 最多取3条最相关的
   - 把它们拼接成一段上下文文本
6. **返回结果**: 如果找不到相关信息或检索失败，就返回空字符串，系统会自动降级为通用模式

这个模块的好处是，当用户回答面试问题时，大模型会参考用户自己的简历和项目经历，回答更具个性化。

## 接口/交互说明

### API端点
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /api/search | 知识库检索 |
| POST | /api/question | 完整问答流程（包含知识库检索） |

### 请求参数
| 参数 | 类型 | 说明 |
|------|------|------|
| query | string | 检索查询词（面试问题） |
| kb_id | string | 知识库ID |
| kb_api_key | string | 知识库API Key（AK:SK格式） |
| project | string | 项目ID（可选） |
| limit | number | 返回数量限制（可选） |
| rerank | boolean | 是否启用重排序（可选） |

### 服务层方法
| 方法 | 说明 |
|------|------|
| search_knowledge(query, kb_id, kb_api_key, **kwargs) | 原始检索调用 |
| get_relevant_knowledge(response) | 结果过滤和拼接 |

### 与其他模块的关系
| 模块 | 关系 |
|------|------|
| Prompt拼接模块 | 知识库结果作为上下文注入Prompt |
| 大模型调用模块 | 最终回答基于知识库上下文生成 |