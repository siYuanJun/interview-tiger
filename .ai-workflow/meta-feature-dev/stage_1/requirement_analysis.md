# Stage 1: 需求澄清 — 路径A: RAG 2.5→3.0

## 1. 项目索引（机械臂 `build_index`）

```
核心检索链路文件:
  backend/app/services/local_knowledge.py   — LocalKnowledgeProvider (单路向量检索)
  backend/app/services/knowledge.py         — VolcengineKnowledgeProvider (云端检索)
  backend/app/routes/question.py            — /question + /question/stream (检索调用入口)
  backend/app/services/prompt.py            — build_messages (三层Prompt模板)
  backend/app/utils/kb_provider.py          — Provider工厂 (local/volcengine切换)
  backend/config.py                         — 配置项 (chunk_size/overlap/model)
```

## 2. 相似已有模块（机械臂 `find_similar`）

> 注意：find_similar 产出来自上一次 M1 工作流的关键词匹配，本次需补充搜索。
>

重新搜索 `hybrid`, `bm25`, `rerank`, `retriev`：

```
find_callers "EnsembleRetriever|BM25Retriever|HyDE|MultiQuery" → 0 references
grep "rerank" → 仅在 knowledge.py (火山引擎云端Rerank，非本地)
grep "bm25\|hybrid\|ensemble" → 代码中 0 references

结论：项目中不存在任何混合检索/BM25/查询改写相关代码，需从零新增。
```

## 3. 需求原文（来自 RAG 升级决策分析 路径A）

### P0: 混合检索（BM25 + Dense 向量 → RRF 融合）
```
当前: 仅 similarity_search_with_score (稠密向量)
目标: EnsembleRetriever(BM25Retriever + Chroma Retriever, RRF fusion)
```

### P0: Query 改写（同义词扩展）
```
当前: 直接使用原始问题文本检索
目标: 对面试问题做同义词扩展后再检索（如「微服」→「微服务」等）
```

### P1: Validator（LLM 判断检索片段相关性）
```
当前: 仅 score < 0.3 阈值过滤（无内容级判断）
目标: 用 LLM 判断检索到的每个片段是否与问题相关
```

### P2: 多轮对话记忆缓存
```
当前: 无对话历史缓存，每次问答独立
目标: 缓存最近 N 轮检索结果，跟进问题可复用上文上下文
```

## 4. 需求边界澄清

### 4.1 范围定义

| 维度 | 本次包含 | 本次不包含 |
|------|---------|-----------|
| 检索方式 | BM25 + Dense 混合检索 | LangGraph 图调度 |
| 查询处理 | 同义词扩展 | Multi-Query/子问题拆解 |
| 结果校验 | LLM 内容级 Validator | 自省反思环 |
| 对话状态 | 多轮记忆缓存 | 状态持久化/Checkpoint |
| 框架迁移 | 保持现有架构 | LCEL 管道重写 |

### 4.2 约束条件

| 约束 | 说明 |
|------|------|
| 延迟 | 单次检索+验证增量 ≤ +500ms |
| 依赖 | 仅新增 `rank-bm25`，不引入新大框架 |
| 兼容 | 不破坏现有火山引擎云端知识库路径 |
| 降级 | BM25 初始化失败静默降级为纯向量检索 |
| 可观测 | 每次检索记录使用了哪些策略 |

### 4.3 验收标准

| # | 标准 | 优先级 |
|---|------|--------|
| AC-01 | 本地知识库检索同时使用 BM25 + 向量检索，RRF 融合排序 | P0 |
| AC-02 | 面试问题中的中文音译词/同义词在检索前自动扩展为标准术语 | P0 |
| AC-03 | 检索结果经 LLM 判断是否与问题相关，无关片段被过滤 | P1 |
| AC-04 | 同一会话中的跟进问题可复用上文检索结果，避免重复检索 | P2 |
| AC-05 | 火山引擎云端知识库路径不受影响 | 兼容 |
| AC-06 | `rank-bm25` 初始化失败时自动降级为纯向量检索 | 降级 |
| AC-07 | 日志记录每次检索的策略组合和耗时 | 可观测 |
