# 变更日志

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