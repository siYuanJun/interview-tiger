# 面试虎项目记忆

## 项目概要
- 名称：面试虎 (interview-tiger)
- 定位：AI 智能面试助手
- 前端：Vue 3 + Vite + Pinia + TypeScript + TailwindCSS
- 后端：Python FastAPI + 火山引擎方舟大模型 + 火山引擎知识库

## 模型与知识库配置（唯一真实来源）
- **大模型**：`deepseek-v4-flash-260425`（后端 `backend/config.py`，前端 `frontend/src/constants.ts`）
- **知识库 ID**：`siyuan_jianli`
- **密钥存储**：`backend/.env`（不提交 Git），`.env.example` 为模板

## Docker 化
- 后端 Docker 启动（`docker compose up -d backend`），前端 Mac 宿主机直接启动
- 桥接网络 `172.30.90.0/24`，静态 IP `172.30.90.10`
- 端口映射 `8001:8000`（8000 被其他容器占用）
- 国产镜像源：`docker.m.daocloud.io/library/python:3.12-slim`

## 双引擎语音识别（ASR）
- **引擎1（优先）**：火山引擎豆包大模型流式语音识别，WebSocket 双向流式
- **引擎2（降级）**：浏览器 Web Speech API，连接失败时自动回退
- 接入地址：`wss://openspeech.bytedance.com/api/v2/asr`
- 音频格式：PCM 16-bit / 16kHz / 单声道
- 后端代理：`backend/app/services/asr.py` + `routes/asr.py`

## 联网搜索降级
- 知识库无结果 → 自动开启联网搜索
- 两种方式：① Bot 应用端点（WEB_SEARCH_BOT_ID）② `enable_search` 参数
- 当前使用方式②（`enable_search=True`）

## 关键文件
- `backend/.env` — 真实密钥（Git 忽略）
- `backend/Dockerfile` / `.dockerignore` — 后端镜像
- `docker-compose.yml` — 后端服务编排
- `scripts/check_mirrors.sh` / `export_images.sh` — 校验与导出
- `frontend/src/composables/useVolcanoASR.ts` — 火山ASR对接
- `docs/模块1-语音识别引擎升级需求文档.md` — ASR需求分析文档

## 启动命令
```bash
# 后端（Docker）
docker compose up -d backend
# 前端（Mac 宿主机）
cd frontend && npm run dev
```

## graphify 知识图谱
- 已初始化（2517 节点，2618 边，193 社区）
- 规则文件：`.codebuddy/rules/graphify.md`（自动加载）
- 分析模块依赖/调用链路/影响面时优先使用 graphify，不逐文件读源码
- 代码变更后运行 `uv tool run --from graphifyy graphify update .`

## RAG 3.0 升级（2026-07-10）
- 使用 meta-feature-dev 7 阶段工作流实施
- 4 个新服务模块：hybrid_retriever / query_rewriter / memory / validator
- 混合检索：LangChain BM25Retriever + Chroma EnsembleRetriever + RRF 融合
- jieba 分词（可选导入，有正则回退）
- Docker 测试策略：`docker exec pip install` 而非重建镜像（避免 PyTorch 重下）
- macOS wheels 与 Linux Docker 不兼容，不要用 pip download 加速

## 用户偏好
- 用户喜欢看到完整的需求分析文档（meta-agent-collaboration 风格）
- 用户喜欢用指令驱动工作流（ai-dev-workflow, meta-feature-dev 等）
- 密钥必须放在配置文件里，不提交Git但本地可用
