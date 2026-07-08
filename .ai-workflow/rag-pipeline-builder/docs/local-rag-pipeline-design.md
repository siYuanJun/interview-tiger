
# 本地 RAG 知识库管道设计文档

## 一、设计目标

为「面试虎」系统构建本地知识库管道，实现与火山引擎知识库的无缝切换，降低 API 调用成本。

## 二、架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    前端交互层                                │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │
│  │ 文档上传    │ │ 切片参数配置 │ │ 知识库类型切换        │ │
│  └──────┬──────┘ └──────┬──────┘ └──────────┬────────────┘ │
└─────────┼────────────────┼──────────────────┼──────────────┘
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI 路由层                           │
│  ┌─────────────────────┐ ┌───────────────────────────────┐ │
│  │ /api/local_kb/upload│ │ /api/local_kb/search          │ │
│  │ /api/local_kb/list  │ │ /api/local_kb/delete          │ │
│  │ /api/local_kb/clear │ │ /api/search (动态路由)         │ │
│  └─────────┬───────────┘ └──────────────────┬────────────┘ │
└────────────┼────────────────────────────────┼──────────────┘
             ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    服务层 (策略模式)                          │
│                                                             │
│  ┌──────────────────────────┐                               │
│  │    KnowledgeProvider     │  ← Protocol 接口              │
│  │  ┌────────────────────┐  │                               │
│  │  │ search(query)      │  │                               │
│  │  │ list()             │  │                               │
│  │  │ upload(file, args) │  │                               │
│  │  │ delete(id)         │  │                               │
│  │  │ clear()            │  │                               │
│  │  └────────────────────┘  │                               │
│  └──────────────┬───────────┘                               │
│                 │                                           │
│     ┌───────────┴───────────┐                               │
│     ▼                       ▼                               │
│  ┌─────────────┐      ┌──────────────┐                      │
│  │ Volcengine  │      │   LocalKB    │                      │
│  │  Provider   │      │   Provider   │                      │
│  └─────────────┘      └──────┬───────┘                      │
│                              │                               │
└──────────────────────────────┼──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    本地 RAG 管道                             │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────┐    │
│  │Document     │───▶│Text         │───▶│ Embedding     │    │
│  │Loaders      │    │Splitters    │    │ (bge-large-zh)│    │
│  └─────────────┘    └─────────────┘    └───────┬───────┘    │
│                                                │             │
│                        ┌───────────────────────▼───────┐     │
│                        │      ChromaDB Vector Store    │     │
│                        │  ┌─────────────────────────┐  │     │
│                        │  │ 向量索引(HNSW) + BM25    │  │     │
│                        │  │ 双路召回                  │  │     │
│                        │  └─────────────────────────┘  │     │
│                        └───────────────┬───────────────┘     │
│                                        │                     │
│                        ┌───────────────▼───────────────┐     │
│                        │         精排(Cross-Encoder)   │     │
│                        │         MMR去重               │     │
│                        └───────────────┬───────────────┘     │
│                                        ▼                     │
│                           ┌─────────────────────┐           │
│                           │  返回 Top-K 结果    │           │
│                           └─────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 三、核心组件设计

### 3.1 Document Loaders

| 文件类型 | Loader 类型 | 依赖包 | 说明 |
|---------|------------|--------|------|
| PDF | PyPDFLoader | pypdf | 支持多页 PDF 解析 |
| TXT | TextLoader | - | 纯文本文件 |
| MD | TextLoader | - | Markdown 文件 |
| DOCX | Docx2txtLoader | python-docx | Word 文档 |
| JSON | JSONLoader | - | JSON 格式数据 |

### 3.2 Text Splitters

**策略选择**：递归字符切片（RecursiveCharacterTextSplitter）

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| chunk_size | 500 | 200-2000 | 切片大小（字符数） |
| chunk_overlap | 50 | 0-200 | 重叠字符数 |
| length_function | len | - | 长度计算函数 |
| separators | ["\n\n", "\n", "。", "！", "？", "；", " ", ""] | - | 分割优先级 |

**设计理由**：面试文档以结构化文本为主，递归切片能保留语义完整性，优先按段落分割。

### 3.3 Embedding 模型

**选型**：bge-large-zh-v1.5

| 维度 | 评估 |
|------|------|
| 检索质量 | ✅ 中文语义理解优秀 |
| 成本 | ✅ 开源免费 |
| 延迟 | ⚠️ 模型较大，首次加载较慢 |
| 中文生态 | ✅ 专为中文优化 |

**备选方案**：
- bge-base-zh-v1.5（较小，速度快）
- text2vec-base-chinese（轻量）

### 3.4 向量库

**选型**：ChromaDB

| 维度 | 评估 |
|------|------|
| 规模支持 | ✅ <100K 文档完全适用 |
| 部署复杂度 | ✅ 嵌入式，无需独立服务 |
| 持久化 | ✅ 支持磁盘持久化 |
| 索引策略 | ✅ HNSW 索引，低延迟 |

**数据目录**：`./backend/data/chroma`

### 3.5 检索管道

**三段式检索**：

```
用户查询 → 查询改写 → 多路召回 → 粗排 → 精排 → MMR去重 → 返回结果
```

| 阶段 | 实现 | 参数 |
|------|------|------|
| 查询改写 | 简单处理（去除标点、大小写） | - |
| 多路召回 | 向量检索 + BM25 | Top-50 |
| 粗排 | ChromaDB 内置排序 | - |
| 精排 | Cross-Encoder（可选） | Top-10 |
| MMR去重 | LangChain MMRChain | diversity=0.3 |

**降级策略**：向量检索为空时回退到全文搜索。

## 四、API 设计

### 4.1 本地知识库 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/local_kb/upload` | 上传文档到本地知识库 |
| GET | `/api/local_kb/list` | 获取已上传文档列表 |
| DELETE | `/api/local_kb/delete/{doc_id}` | 删除指定文档 |
| DELETE | `/api/local_kb/clear` | 清空本地知识库 |
| POST | `/api/local_kb/search` | 检索本地知识库 |

### 4.2 上传请求

```json
{
  "files": "multipart/form-data",
  "chunk_size": 500,
  "chunk_overlap": 50
}
```

### 4.3 搜索请求

```json
{
  "query": "面试问题",
  "top_k": 5
}
```

### 4.4 搜索响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "chunks": [
      {
        "content": "文档内容片段...",
        "score": 0.85,
        "doc_name": "简历.pdf",
        "doc_id": "abc123"
      }
    ]
  }
}
```

## 五、文件结构

```
backend/
├── app/
│   ├── services/
│   │   ├── knowledge.py          # 知识库提供者接口 + 火山引擎实现
│   │   └── local_knowledge.py    # 本地知识库实现
│   ├── routes/
│   │   └── local_kb.py           # 本地知识库路由
│   └── utils/
│       └── kb_provider.py        # 知识库提供者工厂
├── data/
│   └── chroma/                   # ChromaDB 数据目录
└── requirements.txt              # 新增依赖
```

## 六、依赖清单

| 依赖 | 版本 | 用途 |
|------|------|------|
| langchain | ^0.2.0 | 文档加载、切片、检索管道 |
| chromadb | ^0.5.0 | 本地向量存储 |
| sentence-transformers | ^3.0.0 | Embedding 模型 |
| pypdf | ^4.0.0 | PDF 解析 |
| python-docx | ^1.0.0 | Word 文档解析 |
| fastapi | ^0.110.0 | 保持现有版本 |

## 七、性能优化

### 7.1 缓存策略

| 缓存项 | TTL | 说明 |
|--------|-----|------|
| Embedding 结果 | 15min | Redis 缓存（可选） |
| 检索结果 | 5min | 同 query 短时间重复查询 |

### 7.2 索引优化

- 使用 HNSW 索引（ChromaDB 默认）
- 设置 `hnsw:space="cosine"`（余弦相似度）

### 7.3 限制策略

| 限制项 | 值 | 说明 |
|--------|-----|------|
| 单次上传文件数 | 10 | 避免批量上传过大 |
| 单文件大小 | 50MB | 防止内存溢出 |
| 返回结果数 | 5 | 控制响应大小 |

## 八、生产硬化

### 8.1 监控指标

| 指标 | 采集方式 | 告警阈值 |
|------|---------|---------|
| 检索延迟 P50 | Prometheus | >500ms |
| 检索延迟 P99 | Prometheus | >2000ms |
| 召回率 | 自定义指标 | <80% |
| 向量库内存占用 | Prometheus | >80% |

### 8.2 降级策略

1. **向量库不可用** → 回退到全文搜索（BM25）
2. **Embedding 模型加载失败** → 返回错误提示
3. **磁盘空间不足** → 拒绝上传，提示清理

### 8.3 数据备份

- 定期备份 `./backend/data/chroma` 目录
- 支持导出/导入知识库数据

## 九、与现有系统集成

### 9.1 策略模式集成

```python
# knowledge.py
from abc import ABC, abstractmethod

class KnowledgeProvider(ABC):
    @abstractmethod
    def search(self, query: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def upload(self, files, **kwargs) -> dict:
        pass

class VolcengineKnowledgeProvider(KnowledgeProvider):
    # 封装现有 knowledge.py 逻辑
    pass

class LocalKnowledgeProvider(KnowledgeProvider):
    # 本地知识库实现
    pass
```

### 9.2 动态路由切换

在 `search.py` 和 `question.py` 中，根据 `kb_provider` 配置动态选择提供者：

```python
def get_knowledge_provider(kb_provider: str) -> KnowledgeProvider:
    if kb_provider == "local":
        return LocalKnowledgeProvider()
    else:
        return VolcengineKnowledgeProvider()
```

### 9.3 前端配置扩展

`ConfigModal.vue` 需要增加：
- 知识库类型选择器（火山引擎 / 本地）
- 本地模式下显示文档上传区域
- 切片参数配置
- 已上传文档列表

## 十、风险与应对

| 风险 | 等级 | 应对措施 |
|------|------|---------|
| Embedding 模型下载慢 | 中 | 首次启动预下载，提供进度提示 |
| 大文件内存占用 | 中 | 流式处理，分片解析 |
| ChromaDB 数据损坏 | 低 | 定期备份，支持重建索引 |
| 检索效果不如火山引擎 | 中 | 提供质量评估工具，可切换回火山引擎 |

---

**文档版本**：v1.0  
**创建日期**：2026-07-08  
**设计依据**：模块8需求文档 + rag-pipeline-builder 八大原则
