# RAG 完整进化史（时间线 + 代际划分 + 框架对应）

> 结合 LangChain / LangGraph / Deep-Agents 对应关系，梳理 RAG 技术从 2020 论文奠基到 2026 前沿新范式的完整进化历程。

---

## 前置起源（2020 论文奠基）

Meta 发布论文《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》，**正式定义 RAG**，证明「外部检索 + 大模型生成」能解决模型知识过期、幻觉问题，此时仅停留在学术实验，无工程落地。

---

## 第一代：Naive RAG 朴素RAG（2022末–2023上半年，RAG 1.0）

### 核心架构（固定线性流水线）

```
文档固定分块 → 向量化存入向量库 → 用户Query向量匹配召回TopK文档 → 全部拼接进Prompt → LLM一次性输出答案
```

### 代表工具

早期 LangChain 老旧 Chain、简易向量库脚本

### 优点

实现最简单，几行代码就能搭建，适合简单 FAQ

### 致命痛点

1. 固定长度切块，割裂完整语义
2. 仅单一向量检索，关键词精准内容召回差
3. 单次检索、无过滤、无校验，大量无关噪声混入上下文
4. 完全被动流程：不管资料够不够、对不对，直接生成，幻觉严重
5. 复杂多跳推理问题完全无解

---

## 第二代：Advanced RAG 进阶RAG（2023中–2023年底，RAG 2.0）

业界大规模落地，全链路优化检索精度，**只优化单次检索链路，没有闭环**。

### 四大优化模块

| 模块 | 说明 |
|------|------|
| **索引层升级** | 语义分块、分层分块、标题感知切块 |
| **查询预处理（Pre-Retrieval）** | HyDE、Multi-Query、Step-Back Query 改写 |
| **混合检索 Hybrid Search** | 稠密向量检索 + BM25 关键词检索融合 |
| **后处理精排（Post-Retrieval）** | Cross-Encoder Rerank、元数据过滤、冗余片段去重 |

### 代表工具

LangChain LCEL（管道新版语法）、LlamaIndex 初代

### 局限

依旧是**一次检索、一次生成**线性流程；无法判断检索内容是否够用、是否冲突；不能自动补充检索，多步骤复杂分析依然乏力。

---

## 第三代：Modular RAG 模块化RAG（2024上半年，RAG 3.0）

拆解 RAG 全链路为可插拔独立组件，实现流程自定义。

### 新增核心模块

| 模块 | 说明 |
|------|------|
| **Router 路由** | 区分问答 / 总结 / 数据分析，自动匹配检索策略 |
| **Memory 记忆** | 多轮对话上下文缓存 |
| **Validator 校验器** | 简单判断检索片段相关性 |
| **多工具路由** | 可切换向量库、搜索引擎、SQL 查询 |

### 对应框架

LangChain LCEL 完整生态，支持组件自由拼接

### 短板

仅能预设固定流程，**没有自主决策能力**；遇到资料缺失、答案矛盾，无法自动重新检索，流程写死不能动态分支。

---

## 第四代双分支并行（2024全年，两大技术路线）

### 分支A：GraphRAG 图谱增强RAG（微软 2024 年论文）

解决传统向量检索**无法做实体关系、多跳逻辑推理**的短板：

1. 文档解析提取实体、关系，构建知识图谱
2. 局部检索：匹配相关实体子图；全局检索：全文档摘要做宏观问题
3. 图遍历实现链式推理（A → B → C 关联推导）

**适用场景**：企业档案、法律条文、行业复杂因果分析。

### 分支B：Self-RAG / CRAG 自省式RAG

给 RAG 增加**自我校验闭环**：

- **Self-RAG**：模型自动判断「是否需要检索、检索内容是否可用、答案是否可信」，幻觉高则重新检索
- **CRAG（Corrective RAG）**：检索出错时自动回退联网搜索修正事实

两者依旧是单轮逻辑，没有任务规划、多 Agent 协同。

---

## 第五代：Agentic RAG 智能体RAG（2025–2026，当前最新主流进化版）

也就是 **LangGraph / Deep-Agents 承载的 RAG 形态**，彻底颠覆线性管道，RAG 从「固定流程」变成「自主思考的智能体」。

### 核心革命性升级（和前几代本质区别）

1. **动态多轮检索闭环**
   Agent 自主规划：拆解复杂问题 → 判断缺什么资料 → 改写 Query 多次检索 → 校验结果，循环直到信息充足

2. **多工具协同**
   向量检索、Graph 图谱、联网搜索、SQL、代码解释器自由切换

3. **完整自省反思环**
   生成答案后自动核验事实冲突，发现错误自动回滚重新检索

4. **状态持久化 + 分支/循环逻辑**
   不再只能顺序执行，支持条件分支、循环、子任务拆分，由 LangGraph 图引擎调度

### 分层工具对应关系

| 层级 | 工具 | 说明 |
|------|------|------|
| **底层编排** | LangGraph | 图调度内核，手动定义节点、边、循环 |
| **上层封装** | Deep-Agents | LangChain 官方最新进化套件，封装规划、子Agent、长期记忆 |

### 适用场景

深度行业分析、多文档调研报告、复杂业务推理、自主数字员工、企业私有化知识库复杂问答。

---

## 2026 前沿新范式：上下文检索 Contextual Retrieval

Anthropic 最新方案，不依赖海量向量存储，在分块时嵌入全局文档上下文摘要，大幅减少检索噪声，轻量化 Agentic RAG，降低算力成本，属于 Agentic RAG 的轻量化优化分支。

---

## 完整进化链条极简总结

| 代际 | 时期 | 核心特征 | 代表框架 |
|------|------|----------|----------|
| **Naive RAG** | 2022–2023 | 固定切块 + 单次向量检索 | 老版 LangChain Chain |
| **Advanced RAG** | 2023 | 混合检索 + Query 改写 + Rerank | LangChain LCEL |
| **Modular RAG** | 2024 上 | 可插拔组件自定义流程 | LCEL 完整生态 |
| **GraphRAG / Self-RAG** | 2024 | 图谱推理 / 简单自省校验 | 微软 GraphRAG |
| **Agentic RAG** | 2025–2026 | 自主规划、多轮检索、循环反思 | LangGraph → Deep-Agents |

---

## 框架选型指南

| 场景 | 推荐方案 |
|------|----------|
| 简单知识库 FAQ | 1–3 代 RAG：LangChain + LCEL |
| 复杂多跳、因果推理 | 叠加 GraphRAG |
| 自主迭代、复杂任务、多轮反思 RAG | **LangGraph** |
| 开箱即用、无需手写大量图节点的高阶智能体 RAG | **Deep-Agents** |

---

## 参考资料

- 《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》— Meta, 2020
- 《GraphRAG: Unlocking LLM Discovery on Narrative Private Data》— Microsoft, 2024
- LangGraph 官方文档 — https://langchain-ai.github.io/langgraph/
- Deep-Agents — LangChain 官方 Agent 套件
- Contextual Retrieval — Anthropic, 2026
