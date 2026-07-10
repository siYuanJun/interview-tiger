# Stage 3: 影响评估 — RAG 2.5→3.0

## 调用点分析（机械臂 `find_callers`）

### `fetch_knowledge_sync` — 检索调用入口

```
机械臂: find_callers.py "fetch_knowledge_sync" . --summary
结果:   3 references in 1 file (排除 logs/graphify-out)
        → backend/app/routes/question.py:42 (定义), :76, :132 (调用)
        
结论: 仅 question.py 内部使用，修改范围可控
```

### `provider.search()` — 检索方法接口

```
机械臂: find_callers.py "provider.search" . --summary
结果:   2 references in 1 file (排除 docs/文档)
        → backend/app/routes/question.py:47 (local), :55 (volcengine)
        
结论: search() 是统一抽象接口，内部实现变更对调用方透明
```

### `build_messages` — Prompt 拼接入口

```
机械臂: find_callers.py "build_messages" . --summary
结果:   3 references in 1 file (排除 logs/graphify/tests/docs)
        → backend/app/routes/question.py:9 (import), :89, :143 (调用)
        
结论: 接收 knowledge_context 字符串，Validator 过滤后传入不变，零改动
```

### `LocalKnowledgeProvider` — 受影响的类

```
机械臂: find_callers.py "LocalKnowledgeProvider" . --summary
结果:   2 references in 1 file (排除自身定义)
        → backend/app/utils/kb_provider.py:17, 18 (工厂实例化)

结论: 仅通过工厂模式实例化，无直接外部引用
```

### 依赖图验证

```
机械臂: scan_imports.py --target "app.services.local_knowledge"
结果:   0 dependents (没有任何其他模块直接 import 它)

结论: LocalKnowledgeProvider 是内部实现细节，通过 kb_provider 工厂暴露
      所有调用方通过 provider.search(query) 统一接口访问
      内部新增 BM25/Validator/Memory 对外部调用方完全透明
```

---

## 影响矩阵

| 受影响的文件 | 修改类型 | 风险 | 说明 |
|-------------|---------|------|------|
| `backend/app/services/local_knowledge.py` | **重度修改** | 🟡 中 | 核心改动：search() 内部加入 BM25 + Validator + Memory |
| `backend/app/services/hybrid_retriever.py` | **新增** | 🟢 低 | 独立模块，BM25Retriever + EnsembleRetriever 封装 |
| `backend/app/services/query_rewriter.py` | **新增** | 🟢 低 | 独立模块，同义词词典扩展 |
| `backend/app/services/validator.py` | **新增** | 🟢 低 | 独立模块，LLM 批量相关性判断 |
| `backend/app/services/memory.py` | **新增** | 🟢 低 | 独立模块，Sessions 内存缓存 |
| `backend/app/routes/question.py` | **轻微修改** | 🟢 低 | 传递 session_id 给检索层 |
| `backend/app/services/prompt.py` | **无修改** | 🟢 无 | knowledge_context 接口不变 |
| `backend/app/utils/kb_provider.py` | **无修改** | 🟢 无 | 工厂模式不改 |
| `backend/config.py` | **轻微修改** | 🟢 低 | 新增可选配置项 |

---

## 未受影响的模块（风险排除）

| 模块 | 机械臂证据 | 原因 |
|------|-----------|------|
| 火山引擎知识库 `knowledge.py` | `scan_imports` 无关联 | 本地检索和云端检索完全独立 |
| 前端 Vue 组件 | `find_callers` 0 引用 | 纯后端改动 |
| 数据库 `database.py` | `scan_schema` 0 表 | 无 schema 变更 |
| ASR 语音识别链路 | `scan_imports` 无关联 | 检索链路与识别链路解耦 |
| 面试问题校验 `question_judge.py` | `scan_imports` 无关联 | 不同服务层 |

---

## 风险矩阵

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| BM25 分词效果差（中文） | 🟡 中 | 低 | jieba 分词成熟稳定；降级回纯向量检索 |
| Validator LLM 超时 | 🟡 中 | 低 | 超时 3s 自动跳过；校验为增强功能非必需 |
| 内存缓存膨胀 | 🟢 低 | 低 | 30分钟 TTL 自动过期；最大缓存 50 sessions |
| 混合检索延迟超标 | 🟢 低 | 低 | BM25 为纯内存操作 (<50ms)；Validator 可关闭 |
| 火山引擎路径受影响 | 🟢 极低 | 高 | 通过 kb_provider 工厂隔离，zero-touch |

---

## 总结

| 维度 | 评估 |
|------|------|
| **代码变更范围** | 5 个文件（4 新增 + 1 修改），约 250 行新增 |
| **对外接口影响** | **零**（`provider.search()` 签名不变） |
| **降级能力** | 每个新模块独立可降级（BM25 → 纯向量, Validator → 跳过, Memory → 无缓存） |
| **数据库变更** | **零** |
| **前端变更** | **零** |
| **部署影响** | 仅新增 `jieba` pip 依赖 (~15MB) |
| **兼容性** | 向后完全兼容，无破坏性变更 |
