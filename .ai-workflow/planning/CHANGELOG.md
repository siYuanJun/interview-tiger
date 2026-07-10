# 变更日志

## [1.2.0] - 2026-07-10

### Added
- RAG 3.0 混合检索管线 — BM25+向量混合检索（LangChain BM25Retriever + RRF 融合，BM25权重=0.3）
- 查询扩展模块 — 15 个面试领域同义词映射，最多生成 3 个查询变体
- LLM 内容校验模块 — 批量判断检索片段相关性，3s 超时兜底
- 会话多轮记忆缓存 — TTL=1800s，max=50 会话，追问模式检测（"还有呢""继续说"等）
- session_id 字段 — QuestionRequest 新增会话标识，贯穿全管道
- RAG3 配置项 — 8 个环境变量（HYBRID_ENABLED/QUERY_EXPAND_ENABLED/VALIDATOR_ENABLED 等）
- site-packages 快照备份 — 2.8G tar.gz，Dockerfile 可选解压跳过网络下载
- pip 全局清华源 — `/root/.pip/pip.conf`，所有 pip install 自动走国内镜像

### Fixed
- pydantic 2.6.1 + Python 3.12 兼容性 Bug — langsmith 触发 ForwardRef._evaluate() 崩溃，升级到 2.13.4
- BM25 检索回退 — rank_bm25 缺失导致降级纯向量检索，添加 rank_bm25==0.2.2

### Changed
- local_knowledge.py — 从纯向量检索升级为 4 模块全管道（QueryExpand → Hybrid → Validate → Memory）
- question.py — 新增 session_id 参数支持
- Dockerfile — 条件解压 site-packages 快照 + pip 全局镜像源
- requirements.txt — 新增 jieba/rank_bm25，pydantic 版本放宽

## [1.1.2] - 2026-07-06

### Added
- PostgreSQL 数据库存储 — SQLAlchemy ORM 模型，对话记录持久化到数据库
- 多会话管理 — session_id 字段支持区分不同浏览器会话
- 对话更新接口 — PUT /api/dialogues/{id} 更新回答内容
- 数据库连接配置 — app/database.py 统一管理数据库连接和会话

### Changed
- transcript.py — 从内存存储改为 PostgreSQL 存储，支持会话隔离
- useApi.ts — 添加 sessionId 参数支持，新增 updateDialogue 方法
- InterviewPage.vue — 使用 sessionStorage 保存会话 ID，页面加载时恢复对话

## [1.1.1] - 2026-07-06

### Added
- 实时语音显示模块 — 非 final 识别结果实时显示在对话区域，带"正在识别中"状态
- 2秒停顿自动完成机制 — 语音识别停顿2秒后自动提交并触发大模型回答

### Fixed
- 语音识别延迟问题 — 移除 `if (!result.isFinal) return`，临时结果也实时更新 UI

### Changed
- useSpeech.ts — 添加 pauseTimer 变量和2秒停顿检测逻辑
- InterviewPage.vue — 新增 interimDialogue 临时对话显示，识别完成后自动清除

## [1.1.0] - 2026-07-06

### Added
- 规划工作流初始化 — 创建 STATUS.md、CHANGELOG.md、PROJECT_MAP.md
- Docker 容器化配置 — docker-compose.yml，含 PostgreSQL 和后端服务
- 启动脚本 — start.sh，支持 docker/backend/frontend/all/db/stop/logs/status 命令
- UI 技术风格升级 — 科技主题暗色风格、Lucide 图标、渐变背景、动画效果
- API 接口测试脚本 — tests/test_api.py，覆盖所有核心接口

### Fixed
- API Key 配置不生效 — 后端路由添加 resolve_config() 函数，实现前端参数 > .env > 默认值优先级
- bg-primary 样式未定义 — tailwind.config.js 添加自定义颜色配置

### Changed
- 数据库方案 — 从 localStorage 改为 PostgreSQL 持久化存储
- 部署方式 — 支持 Docker 容器化部署和本地开发两种模式

## [1.0.0] - 2026-07-02

### Added
- 前端项目骨架 — Vue 3 + Vite + Tailwind CSS + Pinia + TypeScript
- 后端项目骨架 — FastAPI + 分层架构（Routes/Services）
- 录音与语音识别 — Web Speech API，实时识别转文字
- 问题判断引擎 — 标点/疑问词/句式/长度四重规则
- 大模型调用 — 火山引擎方舟 API，支持 SSE 流式响应
- 知识库检索 — 火山引擎知识库，SignerV4 签名认证
- 面试对话展示 — 左右分栏布局，打字机效果渲染
- 模块交付文档 — 6 个模块完整文档（流程/设计/摘要/检查清单/测试报告）