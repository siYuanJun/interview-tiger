# TASK-024: RAG 3.0 混合检索升级

> 创建时间：2026-07-10 12:00
> 完成时间：2026-07-10 19:59
> 状态：已完成
> 关联任务ID：TASK-024
> 工作流：meta-feature-dev 7 阶段 + api-test-harness 测试

## 目标

将知识库检索从纯向量检索（RAG 2.5）升级为混合检索管线（RAG 3.0），新增 BM25 关键词检索、查询扩展、内容校验、多轮记忆四个模块。

## 阶段拆分

### 阶段 1：需求分析（meta-feature-dev Stage 1）
- [x] 项目索引扫描，识别相似模块
- [x] 约束与边界文档化
- [x] 产出 7 个验收标准，4 个优先级（P0-P2）

### 阶段 2：方案设计（meta-feature-dev Stage 2）
- [x] 4 个模块各产出 3 个备选方案 + 优劣对比
- [x] 选定：LangChain BM25Retriever+RRF / 词典扩展 / LLM 批量校验 / 内存缓存

### 阶段 3：影响评估（meta-feature-dev Stage 3）
- [x] `scan_imports --target "app.services.local_knowledge"` → 0 个外部依赖
- [x] 5 个文件受影响，零 API 变更

### 阶段 4：详细设计（meta-feature-dev Stage 4）
- [x] 架构图 + 4 个模块接口设计
- [x] 8 个新增配置项定义

### 阶段 5：实施计划（meta-feature-dev Stage 5）
- [x] 7 步实施计划，~3 小时
- [x] **用户批准**：进入 Stage 6 执行

### 阶段 6：代码实施
- [x] `hybrid_retriever.py` — BM25+Dense 混合检索，RRF 融合，jieba 分词（可选回退正则）
- [x] `query_rewriter.py` — 15 个面试领域同义词映射，最多 3 个查询变体
- [x] `memory.py` — 会话级内存缓存，TTL=1800s，max=50，追问模式检测
- [x] `validator.py` — LLM 批量内容校验，3 秒超时兜底，YES/NO 解析
- [x] `local_knowledge.py` — 集成 4 个模块，懒加载初始化，全管道搜素
- [x] `config.py` — 新增 8 个 RAG3 环境变量
- [x] `question.py` — 新增 session_id 字段支持
- [x] `requirements.txt` — 添加 jieba、rank_bm25，pydantic 版本放宽

### 阶段 7：Docker 测试与修复
- [x] pydantic 2.6.1 + Python 3.12 兼容性 Bug 修复 → 升级 2.13.4
- [x] rank_bm25 缺失修复 → pip install 0.2.2
- [x] site-packages 全量备份（2.8G tar.gz）
- [x] Dockerfile 优化：pip 全局清华源 + 快照可选回退
- [x] api-test-harness 7/7 全通过（4 非流式 + 3 SSE 流式）

## 问题记录

| 时间 | 问题 | 状态 | 解决方案 |
|------|------|:---:|------|
| ~15:00 | `pip download` 下载了 macOS wheels | 已解决 | macOS wheels 不兼容 Linux Docker，删除后让 Docker 内部下载 |
| ~17:00 | pydantic 2.6.1 ForwardRef._evaluate() 崩溃 | 已解决 | 升级 pydantic 到 2.13.4 |
| ~17:50 | rank_bm25 未安装，BM25 回退纯向量检索 | 已解决 | `pip install rank_bm25==0.2.2` |
| ~18:00 | Docker 重建慢（PyTorch ~800MB） | 已规避 | site-packages 快照 + docker exec 直装 |

## 测试结果

```
✅ 基础问答          — knowledge_used=True
✅ RAG3 知识库命中   — knowledge_used=True, 引用本地文档
✅ 跟进问题（多轮记忆）— 命中 SessionMemory 缓存
✅ 参数校验 422      — 正确拒绝空问题
✅ SSE 流式-本地     — status/chunk/done 事件齐全
✅ SSE 流式-火山引擎 — 正常工作
✅ SSE 流式-跟进记忆 — 缓存命中
通过: 7/7
```

## RAG 3.0 模块验证

```
[QueryRewriter]   ✅ 同义词扩展
[Hybrid]          ✅ BM25权重=0.3, RRF 融合
[Validator]       ✅ 6→2, 6→1 片段过滤
[Memory]          ✅ TTL=1800s, 跟进缓存命中
```
