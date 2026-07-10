# Stage 5: 分步指导 — RAG 2.5→3.0

## 实施顺序（依赖图）

```
Step 1: 安装依赖 + 配置
   ↓
Step 2: hybrid_retriever.py (无依赖)
   ↓
Step 3: query_rewriter.py (无依赖)
   ↓
Step 4: memory.py (无依赖)
   ↓
Step 5: validator.py (依赖 app.services.llm)
   ↓
Step 6: local_knowledge.py 集成 (依赖以上 4 个模块)
   ↓
Step 7: 构建验证 + 集成测试
```

---

## Step 1: 安装依赖 + 配置（5分钟）

### 操作
```bash
pip install jieba
```

### 修改 `config.py`
```python
# RAG 3.0
BM25_WEIGHT = 0.3
HYBRID_ENABLED = True
QUERY_EXPAND_ENABLED = True  
VALIDATOR_ENABLED = True
VALIDATOR_TIMEOUT = 3.0
SESSION_MEMORY_ENABLED = True
SESSION_MEMORY_TTL = 1800
```

### 验收
- [ ] `python -c "import jieba; print(jieba.lcut('测试分词'))"` 正常输出

---

## Step 2: `hybrid_retriever.py`（30分钟）

### 创建文件 `backend/app/services/hybrid_retriever.py`

核心内容：
1. `hybrid_tokenize(text)` — jieba 分词包装
2. `HybridRetriever.__init__` — 构建 BM25Retriever + ChromaRetriever + EnsembleRetriever
3. `HybridRetriever.search(query, top_k)` — 调用 ensemble.invoke()
4. 异常处理：BM25 初始化失败 → `self._ready = False` → 外界检测降级

### 验收
- [ ] `from app.services.hybrid_retriever import HybridRetriever` 无报错
- [ ] `hybrid_tokenize("微服务架构设计")` 返回分词列表
- [ ] BM25 初始化失败时 `is_ready()` 返回 False（不影响服务启动）

---

## Step 3: `query_rewriter.py`（20分钟）

### 创建文件 `backend/app/services/query_rewriter.py`

核心内容：
1. `RETRIEVAL_SYNONYMS` — 面试领域检索同义词词典（~20条，覆盖高频术语）
2. `QueryRewriter.expand(query)` — 先用 `correct_terms()` 纠正，再查同义词词典扩展

### 验收
- [ ] `QueryRewriter().expand("微服架构")` 包含 "微服务" 变体
- [ ] `QueryRewriter().expand("数据库")` 包含 "MySQL" 变体
- [ ] 扩展结果不超过 3 个变体

---

## Step 4: `memory.py`（20分钟）

### 创建文件 `backend/app/services/memory.py`

核心内容：
1. `SessionMemory` 类 — `{session_id: {"query": str, "kb_results": str, "timestamp": float}}`
2. `get()` — 读取 + 自动过期清理
3. `set()` — 写入 + 超量淘汰（LRU 简单版）
4. `is_follow_up()` — 跟进问题判断（关键词 + 简单相似度）

### 验收
- [ ] 设置缓存后 `get()` 返回正确内容
- [ ] TTL 超期后 `get()` 返回 None
- [ ] "还有呢" 被识别为跟进问题
- [ ] "怎么实现" （与上次问题无关联）不被识别为跟进

---

## Step 5: `validator.py`（30分钟）

### 创建文件 `backend/app/services/validator.py`

核心内容：
1. Prompt 模板 — 批量判断 N 个片段是否与问题相关
2. `ContentValidator.validate(question, chunks)` — 调用 LLM + 解析 YES/NO
3. 超时降级 — `asyncio.wait_for(timeout=3.0)` 超时则跳过
4. 解析容错 — LLM 返回格式不规范时保留全部片段

### 验收
- [ ] 正常场景：5 个片段输入，返回过滤后的片段列表
- [ ] 超时场景：返回全部片段（不丢失信息）
- [ ] LLM 错误场景：返回全部片段（不抛出异常）

---

## Step 6: `local_knowledge.py` 集成（45分钟）

### 修改 `backend/app/services/local_knowledge.py`

改动点：
1. `__init__` 中初始化 `HybridRetriever`（需要全量文档列表）
2. `search()` 方法重写：
   ```
   ① query_rewriter.expand(query) → 多查询变体
   ② hybrid_retriever.search(each_variant) → 检索去重
   ③ validator.validate(query, chunks) → 过滤无关片段
   ④ memory.set(session_id, query, result) → 缓存
   ⑤ return knowledge_str
   ```
3. `search_with_details()` 同步修改
4. 每个模块的 `Enabled` 开关检查

### 验收
- [ ] 旧接口 `provider.search(query)` 签名不变，调用方零修改
- [ ] 火山引擎云端知识库路径 `provider.search(query)` **功能不变**
- [ ] BM25 禁用时回退为纯向量检索
- [ ] Validator 禁用时回退为 Score 阈值过滤
- [ ] Memory 禁用时每次独立检索

---

## Step 7: 构建验证 + 测试（30分钟）

### 验证
```bash
# 后端
python -c "from app.services.local_knowledge import LocalKnowledgeProvider; print('OK')"

# 前端（确认无受影响）
cd frontend && npx vue-tsc --noEmit && npx vite build

# API 测试
curl -X POST http://localhost:8001/api/question \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是微服务架构"}'
```

### 验收
- [ ] 所有 import 无报错
- [ ] 前端构建通过（零错误）
- [ ] `/api/question` 正常返回回答
- [ ] 日志包含 `[Hybrid]` `[Validator]` `[Memory]` 标记
- [ ] 日志中 `knowledge_used=True`（验证混合检索有结果）
- [ ] 火山引擎路径 `/api/question` 使用云端知识库仍正常

---

## 总工时

| Step | 内容 | 工时 |
|------|------|------|
| 1 | 依赖 + 配置 | 5 min |
| 2 | hybrid_retriever.py | 30 min |
| 3 | query_rewriter.py | 20 min |
| 4 | memory.py | 20 min |
| 5 | validator.py | 30 min |
| 6 | local_knowledge.py 集成 | 45 min |
| 7 | 构建 + 测试 | 30 min |
| **合计** | | **~3 小时** |
