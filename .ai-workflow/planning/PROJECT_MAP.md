# 项目结构

## 目录树

```
interview-tiger/
├── .ai-workflow/
│   ├── config/
│   │   └── workflow-state.json          # 工作流状态配置
│   ├── docs/
│   │   ├── ARCHITECTURE-OVERVIEW.md     # 架构总览
│   │   ├── DOCS-INDEX.md                # 文档导航索引
│   │   └── LESSONS-LEARNED.md           # 经验知识库
│   ├── planning/
│   │   ├── STATUS.md                    # 项目进度状态
│   │   ├── CHANGELOG.md                 # 变更日志
│   │   └── PROJECT_MAP.md               # 本文件
│   ├── prd/
│   │   ├── tech-requirements.md         # PRD技术需求转化
│   │   └── 模块1-语音识别引擎升级需求文档.md  # ASR升级需求
│   ├── reports/                         # 模块交付文档（6个模块×5份）
│   └── tasks/
│       └── INDEX.md                     # 任务清单与依赖关系
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI 入口
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── asr.py                   # ASR WebSocket 路由
│   │   │   ├── config.py                # 配置接口 (GET/POST)
│   │   │   ├── generate.py              # 大模型生成接口
│   │   │   ├── health.py                # 健康检查 (GET)
│   │   │   ├── question.py              # 问题处理接口 (POST/stream)
│   │   │   ├── search.py                # 知识库检索接口 (POST)
│   │   │   └── transcript.py            # 对话记录接口 (POST/GET)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── asr.py                   # ASR 服务
│   │   │   ├── knowledge.py             # 知识库检索服务
│   │   │   ├── llm.py                   # 大模型调用服务
│   │   │   ├── prompt.py                # Prompt 拼接服务
│   │   │   └── question_judge.py        # 问题判断服务
│   │   └── utils/
│   │       └── __init__.py
│   ├── .dockerignore
│   ├── .env.example                     # 环境变量示例
│   ├── Dockerfile                       # 后端容器构建
│   ├── config.py                        # 配置加载
│   └── requirements.txt                 # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   └── main.css                 # 全局样式（科技主题）
│   │   ├── components/
│   │   │   ├── ConfigModal.vue          # 配置弹窗
│   │   │   ├── DialogueItem.vue         # 对话项组件
│   │   │   ├── HomePage.vue             # 首页
│   │   │   └── InterviewPage.vue        # 面试主页面
│   │   ├── composables/
│   │   │   ├── useApi.ts                # API 调用封装
│   │   │   ├── useRecorder.ts           # 录音逻辑
│   │   │   ├── useSpeech.ts             # 语音识别
│   │   │   └── useVolcanoASR.ts         # 火山引擎 ASR
│   │   ├── router/
│   │   │   └── index.ts                 # 路由配置
│   │   ├── stores/
│   │   │   └── interview.ts             # 面试状态管理
│   │   ├── utils/
│   │   │   └── questionJudge.ts         # 问题判断工具
│   │   ├── App.vue
│   │   ├── constants.ts                 # 常量定义
│   │   └── main.ts                      # Vue 入口
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js               # Tailwind 配置（自定义颜色/动画）
│   └── vite.config.ts                   # Vite 配置
├── tests/
│   └── test_api.py                      # API 接口测试
├── docker-compose.yml                   # Docker Compose 配置
├── start.sh                             # 一键启动脚本
└── README.md
```

## 关键接口

| 接口 | 方法 | 路径 | 入参 | 出参 |
|------|:---:|------|------|------|
| 健康检查 | GET | /api/health | — | {code, message} |
| 获取配置 | GET | /api/config | — | {code, data} |
| 保存配置 | POST | /api/config | {ark_api_key, kb_id, kb_api_key} | {code, message} |
| 知识库检索 | POST | /api/search | {query, kb_id, kb_api_key} | {code, data} |
| 大模型生成 | POST | /api/generate | {prompt, ark_api_key, stream} | {code, data} |
| 问题处理 | POST | /api/question | {question, ark_api_key, kb_id, kb_api_key} | {code, data} |
| 问题处理(流式) | POST | /api/question/stream | {question, ark_api_key, kb_id, kb_api_key} | SSE stream |
| 提交对话记录 | POST | /api/transcript | {content, speaker, session_id} | {code, data} |
| 获取对话列表 | GET | /api/dialogues | {session_id} | {code, data} |
| ASR 流式识别 | WS | /api/asr/stream | PCM 音频流 | 识别文本流 |

## 模块说明

- **routes/**：HTTP/WebSocket 接口层，处理请求路由和参数校验
- **services/**：业务逻辑层，封装外部 API 调用（LLM、知识库、ASR）
- **composables/**：前端组合式 API，封装录音、语音识别、API 调用等逻辑
- **stores/**：Pinia 状态管理，维护面试会话状态
- **components/**：Vue 组件，负责 UI 渲染和用户交互