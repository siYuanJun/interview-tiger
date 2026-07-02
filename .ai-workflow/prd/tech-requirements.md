# PRD技术需求转化 — 面试虎

## 原始PRD摘要

面试虎是一款面向个人求职者的**本地化AI面试辅助工具**。用户在浏览器中打开后，系统通过麦克风实时录制面试官语音，经浏览器原生Web Speech API转为文字，判断是否为有效提问后，调用火山引擎知识库检索用户个人简历/项目经历，拼接成Prompt发送给豆包大模型，生成个性化回答建议并在右侧实时展示。

- **目标用户**：求职者个人使用
- **产品形态**：Web应用（PC + 移动端响应式），纯本地运行，开源
- **核心流程**：开始面试 → 请求麦克风权限 → 实时录音 → 语音识别转文字 → 判断是否为问题 → 检索知识库 → 拼接Prompt → 调用大模型 → 渲染答案 → 继续下一轮

## 功能需求映射表

| PRD功能点 | 技术实现要点 | RESTful API路径 | 涉及端 | 优先级 |
|----------|------------|----------------|--------|--------|
| 首页/面试入口 | HomePage组件，居中布局，"开始面试"按钮 | - | 前端 | P0 |
| 配置管理 | ConfigModal组件，保存ARK_API_KEY/KB_ID/MODEL_ID到localStorage | POST /api/config, GET /api/config | 前端+后端 | P1 |
| 麦克风权限请求 | navigator.mediaDevices.getUserMedia({audio:true}) | - | 前端 | P0 |
| 实时录音 | MediaRecorder API，采集音频流 | - | 前端 | P0 |
| 语音识别转文字 | Web Speech API (SpeechRecognition)，continuous=true, lang=zh-CN | - | 前端 | P0 |
| 问题判断（规则引擎） | 标点/疑问词/句式/长度 四重规则组合判断 | - | 前端 | P1 |
| 问题判断（LLM兜底） | 无法确定时调用大模型二分类 | POST /api/judge | 后端 | P2 |
| 知识库检索 | 后端代理调用火山引擎RAG API（SignerV4签名） | POST /api/search | 后端 | P0 |
| Prompt拼接 | 将知识库结果+面试问题+回答要求拼接为完整Prompt | - | 后端 | P0 |
| 大模型调用（流式） | 调用火山引擎Ark Chat Completions API，stream=true | POST /api/generate | 后端 | P0 |
| 对话展示（左右布局） | InterviewPage组件，PC端左右两栏，移动端上下两栏 | - | 前端 | P0 |
| 流式渲染（打字机效果） | SSE流式接收，逐字渲染回答 | - | 前端 | P1 |
| 状态指示器 | 显示录音中/识别中/生成中状态 | - | 前端 | P1 |
| 结束面试 | 停止录音，保留对话记录，提供导出功能 | - | 前端 | P2 |
| 对话记录导出 | 导出为JSON/TXT/Markdown格式 | GET /api/export | 后端 | P2 |
| 浏览器兼容检测 | 检测SpeechRecognition/MediaRecorder API支持 | - | 前端 | P1 |
| 响应式适配 | Tailwind CSS断点：lg(1024px)/md(768px) | - | 前端 | P1 |
| 健康检查 | 后端服务可用性检测 | GET /api/health | 后端 | P2 |
| 去重机制 | 相同问题30秒内不重复处理（文本相似度判断） | - | 前端 | P2 |

## 工程规范约束

### 架构模式
- 本项目**无数据库**，不适用传统MVCS。采用分层架构：
  - **前端**（Vue 3）：组件层 → Composables层 → API封装层
  - **后端**（FastAPI）：Routes层 → Services层 → 外部API调用层
  - **数据存储**：浏览器localStorage（配置），服务端内存（会话状态）

### API 设计规范
- 遵循 **RESTful API** 规范
  - 资源命名：名词，如 `/api/config`, `/api/search`
  - HTTP方法语义：GET查询，POST创建/处理
  - 统一响应格式：
    ```json
    {
      "code": 0,
      "message": "success",
      "data": {}
    }
    ```
  - 错误码：2xx成功 / 4xx客户端错误 / 5xx服务端错误

### 前端目录结构
```
frontend/
├── src/
│   ├── components/          # 可复用UI组件
│   │   ├── HomePage.vue     # 首页
│   │   ├── InterviewPage.vue # 面试主页面
│   │   ├── ConfigModal.vue  # 配置弹窗
│   │   └── DialogueItem.vue # 单条对话
│   ├── composables/         # 组合式API逻辑
│   │   ├── useRecorder.ts   # 录音逻辑
│   │   ├── useSpeech.ts     # 语音识别
│   │   └── useApi.ts        # API调用
│   ├── stores/              # Pinia状态管理
│   │   └── interview.ts     # 面试状态
│   ├── router/              # 路由
│   ├── api/                 # API封装
│   ├── utils/               # 工具函数
│   ├── App.vue
│   └── main.ts
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

### 后端目录结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI入口
│   ├── routes/
│   │   ├── config.py        # 配置接口
│   │   ├── question.py      # 问题处理接口
│   │   ├── search.py        # 知识库检索接口
│   │   ├── generate.py      # 大模型调用接口
│   │   └── health.py        # 健康检查
│   ├── services/
│   │   ├── knowledge.py     # 知识库检索服务
│   │   ├── llm.py           # 大模型调用服务
│   │   └── prompt.py        # Prompt拼接服务
│   └── utils/
│       └── validator.py     # 参数校验
├── requirements.txt
└── .env.dev
```

### 代码规范
- **前端**：ESLint + Prettier，Vue 3 Composition API风格
- **后端**：PEP 8，类型注解，Pydantic数据校验

## 非功能需求
- **性能**：语音识别延迟 < 2秒；大模型首字延迟 < 5秒
- **兼容性**：Chrome 80+、Edge 80+、Safari 14.1+
- **安全性**：API Key仅存储在localStorage，后端代理转发不暴露
- **可用性**：知识库不可用时自动降级为无知识库模式
- **可维护性**：代码模块化，配置与逻辑分离
- **开源性**：MIT协议

## 技术栈确认
- **前端**：Vue 3 + Vite + Tailwind CSS + Pinia + TypeScript
- **后端**：Python FastAPI + Pydantic
- **外部服务**：火山引擎方舟LLM + 火山引擎知识库
- **部署**：本地启动（npm run dev + uvicorn）
