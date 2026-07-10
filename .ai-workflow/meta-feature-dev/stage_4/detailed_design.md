# Stage 4: 详细设计 — RAG 2.5→3.0

## 架构总览

```
                     POST /question/stream
                           │
                           ▼
                   ┌───────────────┐
                   │  question.py  │
                   │  (不改接口)    │
                   └───────┬───────┘
                           │ provider.search(query)
                           ▼
              ┌────────────────────────┐
              │  LocalKnowledgeProvider│  ← 修改此文件
              │  .search(query)        │
              │                        │
              │  ① query_rewriter      │  ← 新增：同义词扩展
              │     ↓                  │
              │  ② hybrid_retriever    │  ← 新增：BM25+Dense
              │     ↓                  │
              │  ③ validator           │  ← 新增：LLM 校验
              │     ↓                  │
              │  ④ memory              │  ← 新增：会话缓存
              │     ↓                  │
              │  return knowledge_str  │
              └────────────────────────┘
```

## 模块 1: `hybrid_retriever.py` — 混合检索器

### 接口设计

```python
class HybridRetriever:
    """BM25 + Dense 混合检索器 with RRF 融合"""
    
    def __init__(self, vector_store: Chroma, documents: List[Document]):
        """
        Args:
            vector_store: 已有的 ChromaDB 向量库
            documents: 全量文档列表（用于构建 BM25 索引）
        """
        self.vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        self.bm25_retriever = BM25Retriever.from_documents(
            documents, 
            preprocess_func=hybrid_tokenize  # jieba 分词
        )
        self.bm25_retriever.k = 5
        self.ensemble = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.vector_retriever],
            weights=[0.3, 0.7]  # BM25:30%, Dense:70%
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """执行混合检索，返回 RRF 融合排序后的文档"""
    
    def is_ready(self) -> bool:
        """BM25 索引是否就绪（允许降级）"""
```

### 数据流

```
Query → BM25Retriever (jieba分词, k=5) ─┐
                                         ├→ EnsembleRetriever (RRF) → Top K docs
Query → ChromaRetriever (dense, k=5) ────┘
```

### 降级设计

```python
try:
    retriever = HybridRetriever(vector_store, all_docs)
except Exception:
    logger.warning("BM25 初始化失败，回退纯向量检索")
    retriever = None  # search() 检测到 None 时使用旧逻辑
```

---

## 模块 2: `query_rewriter.py` — 查询改写器

### 接口设计

```python
# I.N. 检索同义词词典（与 ASR 术语纠正分开维护）
RETRIEVAL_SYNONYMS: Dict[str, List[str]] = {
    "微服务": ["微服务架构", "分布式服务", "服务化"],
    "数据库": ["SQL", "MySQL", "PostgreSQL", "数据存储"],
    "面试": ["面试技巧", "STAR法则", "面试回答"],
    "项目管理": ["项目经验", "项目经历", "项目背景"],
    # ... 面试场景高频同义词
}

class QueryRewriter:
    def expand(self, query: str) -> List[str]:
        """将原始查询扩展为多个变体
        
        Args:
            query: 原始面试问题文本
        Returns:
            [原始query, 扩展query1, ...] 最多 3 个变体
        """
```

### 数据流

```
Query: "讲讲你做过的微服项目"
  → 复用 correct_terms() 纠正术语 "微服" → "微服务"
  → 查询同义词词典 {"微服务": ["微服务架构", "分布式服务"]}
  → 输出: ["讲讲你做的微服务项目", "讲讲你做的微服务架构项目"]
  → 每个变体分别 hybrid_retriever.search()
  → 去重合并结果
```

### 配置

```python
MAX_EXPANSIONS = 3  # 最多扩展变体数
EXPAND_ENABLED = True  # 全局开关
```

---

## 模块 3: `validator.py` — 内容校验器

### 接口设计

```python
class ContentValidator:
    """用 LLM 批量判断检索片段是否与问题相关"""
    
    def __init__(self, model_id: str = ARK_MODEL, api_key: str = ARK_API_KEY):
        self.model = model_id
        self.api_key = api_key
        self.timeout = 3.0  # 超时秒数
    
    def validate(self, question: str, chunks: List[str]) -> List[str]:
        """批量校验：返回相关片段列表
        
        Args:
            question: 面试问题
            chunks: 检索到的文档片段 [chunk1, chunk2, ...]
        Returns:
            通过校验的相关片段列表
        """
```

### Prompt 设计

```
系统: 你是一个检索结果相关性判断器。
     对每个片段，判断是否与面试问题相关。只回答 YES 或 NO。

问题: {question}

[1] {chunk1[:200]}
[2] {chunk2[:200]}
...

请按编号输出判断结果：
[1] YES
[2] NO
...
```

### 降级与超时

```python
try:
    result = asyncio.wait_for(
        call_llm(validator_prompt, ...), 
        timeout=self.timeout
    )
except (TimeoutError, Exception):
    logger.warning("Validator 超时/失败，保留全部检索结果")
    return chunks  # 不校验，全量返回
```

---

## 模块 4: `memory.py` — 会话记忆

### 接口设计

```python
import time
from typing import Dict, Optional

class SessionMemory:
    """面试会话级的检索结果缓存"""
    
    def __init__(self, ttl_seconds: int = 1800, max_sessions: int = 50):
        self._store: Dict[str, dict] = {}
        self._ttl = ttl_seconds
        self._max = max_sessions
    
    def get(self, session_id: str) -> Optional[dict]:
        """获取会话缓存，自动过期清理"""
    
    def set(self, session_id: str, query: str, kb_results: str):
        """缓存检索结果"""
    
    def is_follow_up(self, session_id: str, new_query: str) -> bool:
        """判断是否为跟进问题（与上次问题语义相关）"""
    
    def _evict_expired(self):
        """淘汰过期条目"""
```

### 跟进问题判断逻辑

```python
def is_follow_up(self, session_id: str, new_query: str) -> bool:
    last = self.get(session_id)
    if not last:
        return False
    
    follow_up_patterns = ["还有呢", "继续", "再详细", "比如说", "举个例子", "那", "另外"]
    
    # 1. 明确跟进关键词
    if any(p in new_query for p in follow_up_patterns):
        return True
    
    # 2. 字符级简单相似度 > 0.5
    if simple_similarity(new_query, last["query"]) > 0.5:
        return True
    
    return False
```

### 生命周期

```
创建 session → 每次检索缓存 → 跟进问题命中缓存 → TTL 30分钟过期
                                                      ↓
                                            新问题触发重新检索
```

---

## 全局配置 (`config.py` 新增项)

```python
# RAG 3.0 混合检索配置
BM25_WEIGHT = 0.3          # BM25 权重 (0.0-1.0), 剩余为向量权重
HYBRID_ENABLED = True       # 混合检索开关
QUERY_EXPAND_ENABLED = True # 查询扩展开关  
VALIDATOR_ENABLED = True    # 内容校验开关
VALIDATOR_TIMEOUT = 3.0     # 校验超时秒数
SESSION_MEMORY_ENABLED = True # 会话记忆开关
SESSION_MEMORY_TTL = 1800   # 记忆过期秒数 (30分钟)
```

---

## 总结

| 新增文件 | 行数估算 | 依赖 |
|----------|---------|------|
| `hybrid_retriever.py` | ~60 | `jieba` (new), `langchain_community.retrievers` |
| `query_rewriter.py` | ~40 | `app.services.question_judge` (正确词库) |
| `validator.py` | ~50 | `app.services.llm` (已有) |
| `memory.py` | ~45 | 无（纯内存） |
| **修改文件** | | |
| `local_knowledge.py` | +30 (search方法重写) | 引入以上 4 个模块 |
| `config.py` | +10 | 无 |
| **总计** | ~230 行新增 | jieba (300KB) |
