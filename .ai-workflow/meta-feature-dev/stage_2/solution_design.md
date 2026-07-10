# Stage 2: 方案设计 — RAG 2.5→3.0 四模块多方案对比

## 依赖图基线（机械臂 `scan_imports`）

```
Top 被依赖模块:
  config(18) > json(14) > sys(14) > logging(13) > vue(12) > ...
  
关键检索链路依赖:
  app.services.llm(2) → 可用于 Validator 的 LLM 调用
  app.utils.kb_provider(3) → Provider 工厂，插入混合检索的理想位置
  app.services.local_knowledge → LocalKnowledgeProvider，需扩展 search() 方法
```

---

## 模块 1: 混合检索（P0）

### 方案对比

| 维度 | 方案 A: rank-bm25 裸库 | 方案 B: LangChain BM25Retriever | 方案 C: Chroma 原生全文 |
|------|------------------------|--------------------------------|------------------------|
| 实现方式 | `from rank_bm25 import BM25Okapi` | `from langchain_community.retrievers import BM25Retriever` + `EnsembleRetriever` | Chrome 默认不支持全文检索 |
| 与 LangChain 集成 | 需手动包装为 Retriever | 原生 EnsembleRetriever(RRF融合) | ❌ 不支持 |
| 依赖 | `pip install rank-bm25` (~50KB) | 已依赖 langchain_community | N/A |
| 分词 | 需手动 jieba 分词 | 内置空格分词（英文），中文需自定义 tokenizer | N/A |
| RRF 融合 | 需手动实现 | `EnsembleRetriever` 内置 RRF | N/A |
| 代码量 | ~80行 | ~40行 | N/A |
| **推荐** | | ✅ **首选** | ❌ |

### 推荐方案：**B — LangChain BM25Retriever + EnsembleRetriever**

**理由**：
1. 项目已使用 `langchain_community`（Chroma, HuggingFaceEmbeddings, document_loaders），零额外依赖
2. `EnsembleRetriever` 内置 RRF 融合算法，无需手写
3. BM25Retriever 需要自定义中文分词器（jieba），但代码量仍然最小
4. 与现有 `LocalKnowledgeProvider.search()` 方法天然兼容

```
方案B 架构:
  ┌──────────────────────────────────────────────────┐
  │            EnsembleRetriever (RRF)                │
  │  ┌─────────────────┐  ┌──────────────────────┐   │
  │  │ BM25Retriever    │  │ Chroma.as_retriever()│   │
  │  │ (keywords:30%)   │  │ (vectors:70%)        │   │
  │  └────────┬────────┘  └──────────┬───────────┘   │
  │           │                      │                │
  │           └──────────┬───────────┘                │
  │                      ▼                            │
  │              RRF 融合排序 (Top K)                  │
  └──────────────────────────────────────────────────┘
```

---

## 模块 2: Query 改写（P0）

### 方案对比

| 维度 | 方案 A: 词典扩展 | 方案 B: LLM改写 | 方案 C: HyDE |
|------|-----------------|----------------|--------------|
| 实现方式 | 复用 `TERM_CORRECTIONS` + 追加检索同义词词典 | `call_llm("把'{query}'扩展为检索友好的形式")` | 让 LLM 生成假设文档再向量化检索 |
| 延迟 | 0ms | +500~800ms | +1~2s |
| Token 成本 | 0 | +1次额外 LLM 调用 | +1~2次额外 LLM 调用 |
| 精准度 | 覆盖已知术语，对未知术语无效 | 覆盖面广，但可能过度改写 | 最高，但成本最高 |
| 代码量 | ~30行 | ~50行 | ~80行 |
| **推荐** | ✅ **首选** | 可选增强 | ❌ 不适合面试场景 |

### 推荐方案：**A — 词典扩展（复用已有基础设施）**

**理由**：
1. 面试虎已有的 `TERM_CORRECTIONS`（~80条）已覆盖面试领域高频音译词
2. 新增 `RETRIEVAL_SYNONYMS`（检索同义词词典）零延迟，仅 CPU 内存操作
3. 面试场景中问题改写需求远低于知识库问答，HyDE 的 ROI 很低
4. 如果未来需要，方案 B（LLM 改写）可作为 option flag 叠加

```
方案A 流程:
  Query → 同义词扩展器 → [原始Query, 扩展Query1, ...] 
       → 每个变体分别检索 → 去重合并 → 返回结果
```

---

## 模块 3: Validator（P1）

### 方案对比

| 维度 | 方案 A: LLM 判断 | 方案 B: Cross-Encoder | 方案 C: 简单规则 |
|------|-----------------|----------------------|-----------------|
| 实现方式 | `call_llm("以下片段是否与问题相关？回答YES/NO")` | 加载 MiniLM-L6 做 rerank | if score > 0.5: valid |
| 准确性 | 高 | 中高 | 低 |
| 延迟 | +300~500ms | +100ms（需加载模型） | 0ms |
| Token 成本 | 每次检索多一次 LLM 调用 | 0 | 0 |
| 依赖 | 无新依赖 | `sentence-transformers` (~100MB) | 无 |
| **推荐** | ✅ **首选** | 可选优化 | ❌ 准确性不足 |

### 推荐方案：**A — LLM Content Validator**

**理由**：
1. 面试虎已有可用的 LLM 基础设施（`call_llm`），零额外集成
2. 面试场景检索结果量小（k=3~5），一次 LLM 调用可批量判断全部分片
3. Cross-Encoder 需要额外下载 100MB+ 模型，增加 Docker 镜像体积
4. 可复用现有 `call_llm` 的降级/超时机制

```
方案A 流程:
  检索结果(5条) → LLM Prompt: "问题=X, 以下片段是否相关? [1], [2], ..." 
              → 返回 [YES, NO, YES, NO, YES] 
              → 过滤后保留相关片段 → 拼接进最终 Prompt
```

---

## 模块 4: 多轮记忆（P2）

### 方案对比

| 维度 | 方案 A: 内存字典 | 方案 B: SQLite 缓存 | 方案 C: Redis |
|------|-----------------|--------------------|---------------|
| 实现方式 | `{session_id: [last_kb_results, ...]}` | SQLite 表存储 session→context | Redis 键值存储 |
| 持久化 | ❌ 进程重启丢失 | ✅ 持久化 | ✅ 持久化 |
| 延迟 | 0ms | ~5ms | ~1ms |
| 编码量 | ~30行 | ~60行 | ~80行 + 部署配置 |
| 依赖 | 无 | 已有 SQLAlchemy | `redis` |
| **推荐** | ✅ **首选** | 后续升级 | ❌ 过度工程 |

### 推荐方案：**A — 内存字典（session_id: context）**

**理由**：
1. 面试场景中对话通常在 30 分钟内完成，内存生命周期足够
2. 知识库规模小（几十到几百切片），缓存全量检索结果无内存压力
3. 如果未来需要持久化记忆，可切换到方案 B（SQLAlchemy 已集成）

```
方案A 数据结构:
  session_context: Dict[str, Dict] = {}
  
  {
    "session_abc123": {
      "last_query": "什么是微服务",
      "last_kb_results": "chunk1\\nchunk2\\n...",
      "timestamp": 1750000000,
      "question_count": 3
    }
  }
  
  逻辑:
  if is_follow_up_question(new_query, session.last_query):
      reuse last_kb_results  # 避免重复检索
  else:
      do_hybrid_search()     # 正常检索
```

---

## 总体方案推荐总结

| 模块 | 方案 | 新依赖 | 延迟增量 | Token 增量 |
|------|------|--------|----------|-----------|
| **混合检索** | LangChain BM25Retriever + RRF | jieba（分词） | +100ms | 0 |
| **Query 改写** | 词典扩展（复用 TERM_CORRECTIONS） | 无 | 0ms | 0 |
| **Validator** | LLM 批量判断 | 无 | +300ms | +1次调用 |
| **记忆** | 内存字典 | 无 | 0ms | 0 |
| **合计** | | jieba (300KB) | +400ms | +1次 LLM 调用/问 |

兼容性：所有方案不修改火山引擎云端知识库路径，仅在 local provider 中生效。

降级策略：BM25 初始化失败 → 回退纯向量检索；LLM Validator 超时 → 跳过校验，保留全部片段。
