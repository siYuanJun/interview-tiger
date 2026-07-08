# RAG 本地知识库踩坑记录

> 日期：2026-07-08  
> 模块：`backend/app/services/local_knowledge.py` + `backend/app/routes/local_kb.py`  
> 技术栈：FastAPI + Python 3.12 + ChromaDB + sentence-transformers + langchain

---

## 踩坑清单

### 坑 1：pydantic 版本与 Python 3.12 不兼容 ⭐⭐⭐⭐⭐

**现象**：所有 `/api/local_kb/*` 接口返回 500，错误信息为：
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**根因**：`pydantic<=2.5.0` 的 v1 兼容层（`pydantic/v1/typing.py`）调用 `ForwardRef._evaluate()` 时缺少 Python 3.12 新增的必选关键字参数 `recursive_guard`。

**错误调用链**：
```
POST /api/local_kb/upload
  → get_knowledge_provider("local")
    → from app.services.local_knowledge import LocalKnowledgeProvider
      → from langchain_community.document_loaders import ...
        → langsmith/schemas.py
          → pydantic/v1/main.py → pydantic/v1/typing.py
            → ForwardRef._evaluate(globalns, localns, set())  ← 少了 recursive_guard
```

**修复**：`requirements.txt` 中 `pydantic` 至少升级到 `>=2.7.0`（最终用的 `2.13.4`）。⚠️ `2.6.1` 也不行，这个 bug 在 v1 兼容层修复较晚。

**教训**：
- ⚠️ Dockerfile 用了 `python:3.12-slim`，但 `requirements.txt` 里的 `pydantic==2.5.0` 不支持 Python 3.12
- ⚠️ 选基础镜像时要把 Python 版本和依赖包的兼容性一起考虑
- ⚠️ **`docker exec pip install` 的修复在 `docker-compose down && up` 后会丢失**——新容器从镜像重建，不会保留运行时安装的包。必须同步更新 `requirements.txt` 并 rebuild 镜像
- ⚠️ `--no-cache` 重建镜像极其缓慢，实际上 `pip install` 进容器再 `restart` 就能验证修复，确认有效后再统一更新 `requirements.txt`

---

### 坑 2：Embedding 模型太大，下载又慢又容易断 ⭐⭐⭐⭐⭐

**现象**：容器启动后首次调用 `/api/local_kb/*` 时，`sentence-transformers` 自动从 HuggingFace 下载 `BAAI/bge-large-zh-v1.5`，容器内网络无法访问 `huggingface.co`。

**模型大小**：

| 模型 | 大小 | 适用场景 |
|------|------|---------|
| `BAAI/bge-large-zh-v1.5` | **~1.3 GB** | 追求极致精度 |
| `BAAI/bge-small-zh-v1.5` | **~100 MB** | 个人/小规模知识库 |

**教训**：
- ⚠️ **永远不要用 large 模型当默认值**。本项目的知识库才几十篇文档、几十 KB，用 1.3GB 的模型是严重过度设计
- ⚠️ **大型模型文件不要依赖运行时从 HuggingFace 自动下载**。容器网络环境不可控（国内经常连不上）
- ⚠️ **需要考虑"离线可用"方案**：
  - 方案 A：预下载模型到宿主机，通过 volume 挂载进容器
  - 方案 B：把模型文件打包进 Docker 镜像（但会让镜像体积暴增）
  - 方案 C：选择无需模型文件的方案（如 LLM Wiki 文件系统直读）
- ⚠️ 模型方案选型前要先评估：**知识库数据量 → 需要多强的检索能力 → 选多大模型**，而不是上来就上 large

---

### 坑 3：Docker 容器无法访问 HuggingFace ⭐⭐⭐⭐

**现象**：`OSError: We couldn't connect to 'https://huggingface.co'`

**根因**：国内网络环境，容器内直连 `huggingface.co` 大概率超时或阻断。

**教训**：
- ⚠️ 所有需要从外网拉取大文件的依赖，都要假设"网络不可用"
- ⚠️ `hf-mirror.com` 作为国内镜像可用，但**模型文件不在 pip 的 `-i` 镜像范围内**，需要单独处理
- ⚠️ 设计 Docker 镜像时，**运行时下载 = 定时炸弹**

---

### 坑 4：依赖链太重，一个小功能拖了一堆包 ⭐⭐⭐

**当前 `local_knowledge.py` 引入的依赖链**：
```
sentence-transformers (含 torch)
  → transformers
  → huggingface_hub
chromadb
  → hnswlib (需 C++ 编译)
  → onnxruntime
langchain / langchain-community / langchain-text-splitters
  → langsmith
  → pydantic
  → 各种 loader (PyPDFLoader, Docx2txtLoader...)
```

**教训**：
- ⚠️ 为了"上传文件→切片→向量化→检索"这一个功能，引入了整个 langchain 生态
- ⚠️ 每一项依赖都是潜在的版本冲突源（这次 pydantic 就是例子）
- ⚠️ **功能需求小 ≠ 依赖应该多**。对于几十篇文档的本地知识库，完全可以用 Python 标准库 + 文件系统实现

---

### 坑 5：`docker-compose build --no-cache` 慢到不可接受 ⭐⭐

**现象**：修一行 `requirements.txt` 后用了 `--no-cache` 重建，等了十几分钟没反应。

**根因**：`--no-cache` 强制重建所有层，包括 apt-get 装系统依赖 + 编译 chromadb 原生扩展 + 下载所有 Python 包。

**教训**：
- ⚠️ `--no-cache` 是核武器，不到万不得已不要用
- ⚠️ Dockerfile 里 `COPY requirements.txt .` 在 `COPY . .` 之前，改 `requirements.txt` 后用普通 `build` 就只会重建依赖安装层
- ⚠️ 实在只想更新一个 pip 包时，`docker exec pip install` + `docker restart` 比 rebuild 快 100 倍

---

### 坑 6：`docker exec pip install` 修复在 `down && up` 后丢失 ⭐⭐⭐⭐

**现象**：用 `docker exec pip install "pydantic>=2.7.0"` 修好了，但下次 `docker-compose down && up` 后又 500 了。

**根因**：`docker exec` 只改运行中的容器文件系统，不影响镜像。`down` 删除容器，`up` 从**旧镜像**重建新容器，`pip install` 的修改全部丢失。

**正确流程**：
1. `docker exec pip install xxx` → 先验证
2. `docker-compose restart` → 让修改生效（**不要 down！**）
3. 确认修复有效 → 同步更新 `requirements.txt`
4. 下次 rebuild 镜像时版本就固化了

**教训**：
- ⚠️ `restart` 保修改，`down && up` 丢修改——记住这条界线
- ⚠️ 任何 `docker exec` 的临时修复，最终都要回归到 `requirements.txt` / Dockerfile

---

### 坑 7：huggingface_hub 强制联网检查，缓存形同虚设 ⭐⭐⭐⭐

**现象**：模型文件已通过 volume 挂载到 `/root/.cache/huggingface/hub/`，但首次调用仍卡住，日志显示在重试连接 `huggingface.co`。

**根因**：`huggingface_hub` 每次加载模型前都会发 HEAD 请求到 `huggingface.co` 确认版本，即使本地缓存完备也会等超时。

**修复**：`docker-compose.yml` 的 backend environment 加：
```yaml
- HF_HUB_OFFLINE=1
```
或在 `.env` 里设：
```bash
HF_HUB_OFFLINE=1
```

**教训**：
- ⚠️ 缓存挂载 ≠ 离线模式。`huggingface_hub` 的"联网先确认"行为是默认开启的
- ⚠️ 所有需要在容器内加载模型的场景，必须同时设置离线标志

---
## 正确的一次性全流程操作

经过所有踩坑后，正确的本地知识库搭建步骤：

```bash
# 1. 宿主机下载模型（走国内镜像）
pip install huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download BAAI/bge-small-zh-v1.5

# 2. docker-compose.yml 三个关键配置：
#    - volumes 挂载 ~/.cache/huggingface:/root/.cache/huggingface
#    - environment 加 HF_HUB_OFFLINE=1
#    - .env 设 LOCAL_KB_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 3. requirements.txt 确保 pydantic>=2.7.0

# 4. 构建并启动
docker-compose build backend && docker-compose up -d backend

# 5. 验证
curl -s http://localhost:8001/api/local_kb/stats
```

---

## 总结：下次选方案前必须问自己

- [ ] 知识库数据量有多大？（几十篇 vs 几万篇，方案完全不同）
- [ ] 模型真的有这么大吗？（small 模型 100MB 够不够用？）
- [ ] 容器能访问所有需要的外部服务吗？（HuggingFace、PyPI...）
- [ ] 依赖链能否砍掉？（真的需要 langchain/chromadb/sentence-transformers 全家桶吗？）
- [ ] 如果 RAG 太重，LLM Wiki 够不够？

> **核心教训：先想清楚场景需要什么，再选工具。不要因为 RAG 是行业主流就默认用它。**
