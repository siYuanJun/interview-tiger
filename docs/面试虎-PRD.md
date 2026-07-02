# 产品需求文档（PRD）

## AI智能面试助手


## 一、产品概述

### 1.1 产品定位

AI智能面试助手是一款面向个人求职者的本地化面试辅助工具。产品在面试过程中实时录制面试官语音，通过语音识别转为文字后，结合用户上传的个人简历与知识库内容，由大模型智能生成贴合个人背景的回答建议，帮助用户在面试中更自信、更从容地应对各类问题。

### 1.2 目标用户

- 正在求职、需要面试辅助的个人用户
- 希望提升面试表现、练习面试回答的求职者

### 1.3 产品形态

- Web应用（PC端 + 移动端响应式适配）
- 纯本地运行，无需部署，开箱即用
- 开源项目

### 1.4 核心价值

- **实时性**：面试官提问后即刻生成回答建议
- **个性化**：回答基于用户自己的简历和知识库，而非通用模板
- **便捷性**：浏览器即可使用，无需安装额外软件


## 二、核心功能流程

### 2.1 整体流程

```
开始面试 → 请求麦克风权限 → 实时录音 → 语音识别转文字 → 
判断是否为问题 → 检索知识库 → 拼接Prompt → 调用大模型 → 
右侧渲染答案 → 继续监听下一轮
```

### 2.2 功能模块

| 模块 | 功能 | 说明 |
|------|------|------|
| 面试控制 | 开始/结束面试 | 点击后请求麦克风权限，开始录音 |
| 语音采集 | 实时录音 | 基于浏览器MediaRecorder API采集麦克风音频 |
| 语音识别 | 语音转文字 | **双引擎**：火山引擎豆包 ASR（优先）→ 浏览器 Web Speech API（降级回退） |
| 问题判断 | 识别是否为疑问句 | 判断识别出的文本是否为面试官提问 |
| 知识库检索 | RAG检索 | 调用火山引擎知识库接口，检索与问题相关的个人资料 |
| 答案生成 | 大模型推理 | 调用火山引擎大模型接口，生成个性化回答 |
| 对话展示 | 左问题/右答案 | 左侧展示面试官问题，右侧展示AI生成的回答建议 |
| 配置管理 | API Key/知识库配置 | 用户配置火山引擎API密钥和知识库ID |


## 三、技术架构

### 3.1 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Vue 3 + Vite | 响应式UI框架，支持PC/移动端 |
| 前端UI | Tailwind CSS / Element Plus | 快速构建简洁界面 |
| 前端录音 | MediaRecorder API + Web Audio API | 浏览器原生录音能力 |
| 前端语音识别 | 火山引擎豆包 ASR + Web Speech API（降级） | **双引擎**：AudioContext PCM → 后端 WebSocket → 火山引擎实时识别；失败时自动回退浏览器原生识别 |
| 后端 | Python + FastAPI | 轻量级后端服务 |
| 后端语音代理 | WebSocket 代理 | 前端 ↔ 后端 ↔ 火山引擎 ASR 三层 WebSocket 转接 |
| 大模型 | 火山引擎方舟平台 (DeepSeek V4 Flash) | 文本生成 + 联网搜索降级 |
| 知识库 | 火山引擎企业知识引擎 (RAG API) | 知识库检索增强生成 |
| 部署方式 | Docker (后端) + Mac宿主机 (前端) | docker compose up + npm run dev |

### 3.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端 (Vue 3)                        │
│  ┌──────────┐  ┌───────────────────┐  ┌──────────────┐    │
│  │ 录音模块  │→│ 语音识别模块       │→│ 对话展示     │    │
│  │(Audio-   │  │(豆包ASR优先       │  │ (左/右)      │    │
│  │ Context) │  │ WebSpeech降级)    │  │ 问题 | 答案  │    │
│  └──────────┘  └───────────────────┘  └──────────────┘    │
│                       │ PCM→WebSocket                     │
└───────────────────────┼───────────────────────────────────┘
                        │ WebSocket /api/asr/stream
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                      后端 (Python FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ ASR代理模块  │  │ 问题判断模块  │→│ Prompt拼接模块   │  │
│  │(WebSocket    │  │(疑问句识别)  │  │(知识库上下文注入)│  │
│  │ 转接火山ASR) │  └──────────────┘  └──────────────────┘  │
│  └──────────────┘                        ↓                 │
│       ↓ WebSocket               ┌──────────────────┐       │
└──────┼──────────────────────────│   API调用模块    │───────┘
       ↓                          └──────────────────┘       │
┌──────────────────┐                        ↓                 │
│  火山引擎ASR     │              ┌───────────────────────┐   │
│  (豆包语音同款)  │              │  火山引擎大模型       │   │
│  实时语音→文字   │              │  DeepSeek V4 Flash    │   │
│  WebSocket流式  │              │  + 联网搜索降级       │   │
└──────────────────┘              └───────────────────────┘   │
                                     ┌─────────────────┐     │
                                     │ 火山引擎知识库  │     │
                                     │ RAG检索个人资料 │     │
                                     └─────────────────┘     │
```


## 四、详细功能说明

### 4.1 页面设计

#### 4.1.1 首页（面试前）

- **核心元素**：一个显眼的“开始面试”按钮
- **配置入口**：右上角设置图标，点击可配置：
  - 火山引擎API Key（ARK_API_KEY）
  - 知识库ID（kb_id）
  - 选择的模型ID（如 doubao-seed-2-1-pro-260628）
- **页面风格**：极简设计，居中布局

#### 4.1.2 面试页面（进行中）

- **布局**：左右两栏（PC端） / 上下两栏（移动端）
  - **左侧**：面试官问题列表（按时间顺序排列）
  - **右侧**：AI回答建议列表（与左侧问题一一对应）
- **状态指示器**：顶部显示录音状态（录音中/识别中/生成中）
- **控制按钮**：底部“结束面试”按钮

### 4.2 录音与语音识别模块

#### 4.2.1 技术方案

采用**双引擎方案**，火山引擎豆包 ASR 优先，浏览器 Web Speech API 降级回退：

**引擎1（优先）：火山引擎豆包大模型流式语音识别**

- 豆包输入法同款引擎，中文识别精度高
- 通过 WebSocket 双向流式实时识别（边说话边出文字）
- 音频格式：PCM 16-bit / 16kHz / 单声道
- 连接链路：浏览器 AudioContext → PCM base64 → 后端 WebSocket 代理 → 火山引擎 ASR
- Token 安全：密钥存储在后端 `.env`，不暴露给前端

**引擎2（降级回退）：浏览器 Web Speech API**

- 当火山引擎 ASR 连接失败（未配置密钥、服务不可用）时自动回退
- 仅支持 Chrome 80+ / Edge 80+，其他浏览器不可用
- 无额外成本，识别精度一般

#### 4.2.2 关键配置

**火山引擎 ASR 配置**：

```bash
# backend/.env
ASR_APP_ID=your_asr_app_id       # 火山引擎语音识别应用ID
ASR_TOKEN=your_asr_token          # 火山引擎语音识别Token
```

**浏览器 Web Speech API 配置**（降级时自动生效）：

```javascript
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = true;      // 持续识别模式
recognition.interimResults = true;  // 返回临时结果
recognition.lang = 'zh-CN';         // 中文识别
```

#### 4.2.3 ASR WebSocket 接口

- **前端 → 后端**：WebSocket `/api/asr/stream`
  - 发送：`{"type": "audio", "data": "<base64 PCM>"}` 或 `{"type": "finish"}`
- **后端 → 火山引擎**：WebSocket `wss://openspeech.bytedance.com/api/v2/asr`
  - 自定义二进制帧协议：4字节头 + 4字节载荷大小 + gzip压缩数据
  - 认证：`Authorization: Bearer;{Token}`
- **后端 → 前端**：
  - 返回：`{"type": "result", "text": "识别文本", "is_final": false/true}`
  - 错误：`{"type": "error", "message": "错误信息"}`

#### 4.2.4 识别结果处理

- 实时获取识别文本（增量返回，非全量）
- 通过防抖/节流控制发送频率，避免频繁请求
- 区分临时结果（`is_final: false`）和最终结果（`is_final: true`），仅在最终结果稳定后触发后续流程
- 火山引擎 ASR 连接失败时，自动回退到浏览器 Web Speech API

### 4.3 问题判断模块

#### 4.3.1 判断逻辑

系统需要判断识别出的文本是否为面试官的**有效提问**，而非用户自己的回答、语气词或无效语音。

**判断策略（多重规则组合）** ：

1. **标点符号规则**：以“？”、“吗”、“呢”等疑问语气词结尾
2. **疑问词规则**：包含“什么”、“怎么”、“为什么”、“如何”、“哪”、“谁”、“多少”等疑问词
3. **句式规则**：以“请问”、“我想问”、“能说一下”等典型提问句式开头
4. **长度规则**：文本长度 > 3个字符（过滤语气词和无效语音）
5. **大模型辅助判断**（兜底方案）：将文本送入大模型进行二分类判断（“是问题”/“不是问题”），仅在前4条规则无法确定时触发

#### 4.3.2 去重机制

- 相同或高度相似的问题在短时间内（如30秒）不重复处理
- 使用文本相似度（如编辑距离或余弦相似度）进行判断

### 4.4 知识库检索模块

#### 4.4.1 火山引擎知识库接口

调用火山引擎企业知识引擎的RAG检索接口。

**接口信息**：

- **请求方式**：POST
- **请求地址**：`{{domain}}/profile_platform/api/v2/rag/search`
- **认证方式**：Bearer Token（API_KEY）
- **请求头**：
  - `Authorization: Bearer {API_KEY}`
  - `x-tenant: {项目ID}`
  - `x-org: {主账号ID}`
  - `Content-Type: application/json`

**请求参数**：

| 参数 | 类型 | 必传 | 说明 |
|------|------|------|------|
| kb_id | string | 是 | 知识库ID |
| query | string | 是 | 检索问题文本 |
| top_k | int | 否 | 返回最相关的前K个切片，默认5 |

#### 4.4.2 知识库内容说明

用户需提前在火山引擎控制台完成：
1. 创建知识库
2. 上传个人资料（简历PDF/Word、项目经历、个人介绍等）
3. 等待文档解析完成

系统仅负责调用检索接口，不涉及知识库的创建与管理。

### 4.5 Prompt拼接模块

#### 4.5.1 拼接策略

系统将面试官问题与知识库检索结果拼接成完整的Prompt，发送给大模型。

**Prompt模板**：

```
你是一位资深的面试辅导专家。请根据以下信息，为求职者生成一个针对面试问题的回答建议。

【求职者背景信息】
{知识库检索结果}

【面试官问题】
{面试官提出的问题}

【回答要求】
1. 回答要结合求职者的真实背景，体现个人特色，不要使用通用模板
2. 回答结构清晰（可采用STAR法则：情境-任务-行动-结果）
3. 语气自信、专业、诚恳
4. 回答时长控制在1-3分钟（约200-500字）
5. 如果问题涉及求职者简历中没有的内容，请诚实建议如何得体回应

请生成回答建议：
```

#### 4.5.2 知识库为空时的降级方案

若知识库未配置或检索无结果，Prompt降级为：

```
你是一位资深的面试辅导专家。请针对以下面试问题，生成一个专业、结构清晰的回答建议。

【面试官问题】
{面试官提出的问题}

【回答要求】
1. 回答要专业、有逻辑、体现思考深度
2. 采用STAR法则组织回答
3. 语气自信、诚恳
4. 回答时长控制在1-3分钟

请生成回答建议：
```

### 4.6 大模型调用模块

#### 4.6.1 火山引擎大模型接口

采用火山方舟 **Responses API**（推荐）或 Chat API。

**Responses API 接口信息**：

- **请求方式**：POST
- **请求地址**：`https://ark.cn-beijing.volces.com/api/v3/responses`
- **认证方式**：`Authorization: Bearer {ARK_API_KEY}`
- **SDK安装**：`pip install 'volcengine-python-sdk[ark]'`

**请求示例（Python）** ：

```python
import os
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.getenv('ARK_API_KEY'),
)

response = client.responses.create(
    model="doubao-seed-2-1-pro-260628",  # 用户可配置
    input=prompt,  # 拼接好的完整Prompt
)

answer = response.output_text
```

**Chat API 接口信息**（备选方案）：

- **请求地址**：`https://ark.cn-beijing.volces.com/api/v3/chat/completions`
- **请求方式**：POST
- **认证方式**：`Authorization: Bearer {ARK_API_KEY}`

#### 4.6.2 流式输出

为提升用户体验，建议启用流式输出（`stream: true`），让回答逐字/逐句在右侧渲染，而非一次性全部显示。

### 4.7 对话展示模块

#### 4.7.1 数据结构

每条对话记录包含：

```typescript
interface DialogueItem {
  id: string;           // 唯一标识
  question: string;     // 面试官问题
  answer: string;       // AI生成回答
  timestamp: number;    // 时间戳
  status: 'generating' | 'done'; // 生成状态
}
```

#### 4.7.2 渲染逻辑

- 左侧按时间顺序展示问题列表
- 右侧同步展示对应的回答
- 回答生成过程中显示加载动画（如打字机效果）
- 新问题出现时自动滚动到最新位置

### 4.8 响应式设计

#### 4.8.1 断点设计

| 屏幕宽度 | 布局 |
|----------|------|
| ≥ 1024px | 左右两栏（问题 | 答案） |
| 768px - 1023px | 左右两栏（比例调整） |
| < 768px | 上下两栏（问题上 | 答案下） |

#### 4.8.2 移动端适配要点

- 按钮尺寸放大（触控友好）
- 字体大小适配
- 底部固定操作栏
- 横屏/竖屏适配


## 五、接口设计

### 5.1 前后端接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 配置保存 | POST | /api/config | 保存API Key、知识库ID等 |
| 配置获取 | GET | /api/config | 获取当前配置 |
| 语音识别 | WebSocket | /api/asr/stream | PCM音频流式识别（前端→后端→火山引擎ASR代理） |
| 问题处理 | POST | /api/question | 接收问题文本，返回AI回答 |
| 问题处理(流式) | POST | /api/question/stream | SSE流式返回AI回答 |
| 知识库检索 | POST | /api/search | 检索知识库（后端代理调用火山引擎） |
| 大模型调用 | POST | /api/generate | 生成回答（后端代理调用火山引擎） |
| 健康检查 | GET | /api/health | 服务状态检查 |

### 5.2 核心接口详细定义

#### POST /api/question

**请求体**：

```json
{
  "question": "你这边都会什么技术栈？"
}
```

**响应体**：

```json
{
  "code": 0,
  "data": {
    "answer": "我主要专注于Java后端开发...",
    "knowledge_used": true,  // 是否使用了知识库
    "source_chunks": []      // 引用的知识库片段（可选）
  },
  "message": "success"
}
```

#### POST /api/search

**请求体**：

```json
{
  "query": "你这边都会什么技术栈？",
  "top_k": 5
}
```

**响应体**：

```json
{
  "code": 0,
  "data": {
    "chunks": [
      {
        "content": "熟悉SpringBoot、SpringCloud...",
        "score": 0.92,
        "doc_name": "我的简历.pdf"
      }
    ]
  }
}
```

#### POST /api/generate

**请求体**：

```json
{
  "prompt": "完整的Prompt文本",
  "stream": true
}
```

**响应体**（流式）：

```
data: {"chunk": "我主要"}
data: {"chunk": "专注于"}
data: {"chunk": "Java后端开发..."}
data: [DONE]
```


## 六、难点与对策

### 6.1 语音识别准确率

**难点**：面试环境可能存在噪音、口音、语速差异，浏览器原生Web Speech API的识别准确率有限。

**对策**：
- **已实现**：接入火山引擎豆包大模型流式语音识别（与豆包输入法同引擎），中文识别精度显著提升
- **降级机制**：火山引擎 ASR 连接失败时自动回退到浏览器 Web Speech API
- 提示用户在安静环境使用
- 启用`interimResults`显示实时识别过程，让用户感知识别状态
- 在设置中提供麦克风音量检测和调试功能

### 6.2 问题判断的准确性

**难点**：如何准确区分面试官的提问与用户的回答、寒暄、语气词等。

**对策**：
- 采用多重规则组合判断（标点+疑问词+句式+长度）
- 大模型二分类作为兜底方案
- 提供手动“标记为问题”的交互能力，让用户纠错
- 持续记录误判case，优化判断规则

### 6.3 回答的实时性与体验

**难点**：大模型推理需要时间（通常3-10秒），可能造成等待焦虑。

**对策**：
- 启用流式输出（`stream: true`），逐字显示回答
- 显示生成状态（“正在检索知识库...” → “正在生成回答...”）
- 右侧回答区域显示打字机效果动画
- 考虑在前端预加载常用问题的回答缓存

### 6.4 知识库检索的时效性

**难点**：知识库文档导入/删除后，需要等待知识库就绪才能检索（最长滞后5秒）。

**对策**：
- 在配置页面提示用户等待知识库就绪
- 提供“测试检索”功能，验证知识库是否可用
- 知识库检索失败时自动降级为无知识库模式

### 6.5 浏览器兼容性

**难点**：Web Speech API在部分浏览器（如Safari部分版本）支持有限。

**对策**：
- **已实现**：火山引擎 ASR 通过后端 WebSocket 代理，前端仅需 AudioContext（全浏览器兼容）
- 火山引擎 ASR 失败时自动回退到浏览器 Web Speech API（仅 Chrome/Edge）
- 在页面启动时检测浏览器兼容性
- 两种方式都失败时，提供手动输入问题文本的备选方案

### 6.6 长对话的上下文管理

**难点**：面试是持续的多轮对话，每轮独立提问可能丢失上下文。

**对策**：
- 在Prompt中注入历史对话摘要（最近2-3轮）
- 利用Responses API的上下文缓存能力
- 设置对话轮数上限，避免Prompt过长

### 6.7 本地部署与数据安全

**难点**：用户数据（简历、面试对话）完全在本地，需保障隐私安全。

**对策**：
- 所有API Key和配置仅存储在浏览器本地（localStorage）
- 不建立任何云端数据库
- 知识库检索和大模型调用均通过本地后端代理，不经过第三方服务
- 开源代码接受社区安全审计


## 七、项目结构

```
ai-interview-assistant/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── HomePage.vue     # 首页（开始面试）
│   │   │   ├── InterviewPage.vue # 面试页面（左右对话）
│   │   │   ├── ConfigModal.vue  # 配置弹窗
│   │   │   └── DialogueItem.vue # 单条对话组件
│   │   ├── composables/
│   │   │   ├── useRecorder.ts   # 录音逻辑
│   │   │   ├── useSpeech.ts     # 语音识别（双引擎：豆包ASR + Web Speech降级）
│   │   │   ├── useVolcanoASR.ts # 火山引擎ASR WebSocket对接层
│   │   │   └── useApi.ts        # API调用逻辑
│   │   ├── stores/
│   │   │   └── interview.ts     # Pinia状态管理
│   │   ├── constants.ts         # 前端常量（模型ID/知识库ID）
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── backend/                     # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI/Flask入口
│   │   ├── routes/
│   │   │   ├── config.py        # 配置接口
│   │   │   ├── question.py      # 问题处理接口
│   │   │   ├── generate.py      # 大模型生成接口
│   │   │   ├── search.py        # 知识库检索接口
│   │   │   ├── asr.py           # 语音识别WebSocket代理
│   │   │   └── health.py        # 健康检查
│   │   ├── services/
│   │   │   ├── knowledge.py     # 知识库检索服务
│   │   │   ├── llm.py           # 大模型调用服务（含联网搜索降级）
│   │   │   ├── asr.py           # 火山引擎ASR WebSocket客户端
│   │   │   └── prompt.py        # Prompt拼接服务
│   ├── requirements.txt
│   ├── Dockerfile               # Docker镜像（国产源）
│   ├── .env                     # 真实密钥（Git忽略）
│   ├── .env.example             # 密钥模板
│   └── config.py                # 集中配置文件
├── scripts/
│   │   ├── export_images.sh     # Docker镜像导出
│   │   └── check_mirrors.sh     # 国产镜像源校验
├── docker-compose.yml           # 后端容器编排（桥接网络+静态IP）
├── docs/
│   │   ├── 面试虎-PRD.md         # 本文档
│   │   ├── 模块1-语音识别引擎升级需求文档.md  # ASR功能需求分析
│   │   └── 字节跳动接口调用指南.md  # API密钥指南（Git忽略）
├── README.md
└── PRD.md                       # 本文档
```


## 八、启动与配置

### 8.1 前置条件

1. 火山引擎账号（已实名认证）
2. 已开通火山方舟大模型服务 + DeepSeek V4 Flash 模型
3. 已创建API Key
4. 已创建知识库并上传文档（知识库ID：siyuan_jianli）
5. 已开通火山引擎语音识别服务（豆包大模型流式语音识别），获取 ASR_APP_ID 和 ASR_TOKEN

### 8.2 本地启动

```bash
# 后端启动（Docker）
docker compose up -d backend

# 前端启动（Mac 宿主机）
cd frontend
npm install
npm run dev
```

### 8.3 环境变量

```bash
# backend/.env（不提交Git）

# 大模型
ARK_API_KEY=your_api_key_here
ARK_MODEL=deepseek-v4-flash-260425

# 知识库
KB_ID=siyuan_jianli
KB_API_KEY=your_ak_sk_here

# 语音识别（豆包同款引擎）
ASR_APP_ID=your_asr_app_id
ASR_TOKEN=your_asr_token

# 联网搜索（可选，知识库无结果时降级）
# WEB_SEARCH_BOT_ID=bot-xxx
```


## 九、非功能需求

| 需求 | 说明 |
|------|------|
| 性能 | 语音识别延迟 < 2秒；大模型首字延迟 < 5秒 |
| 兼容性 | Chrome 80+、Edge 80+、Safari 14.1+ |
| 安全性 | API Key仅存储在本地，不经过任何第三方 |
| 可用性 | 知识库不可用时自动降级，不影响核心功能 |
| 可维护性 | 代码模块化，配置与逻辑分离 |
| 开源性 | MIT/Apache 2.0协议，提供完整README和部署文档 |


## 十、闭环设计（用户遗漏点补充）

| 遗漏点 | 补充方案 |
|--------|----------|
| **如何区分“谁在说话”** | 系统只采集麦克风音频并识别为文字，不区分声纹。用户需自行将麦克风对准面试官方向。建议在UI中提示“请将设备靠近面试官” |
| **回答完如何进入下一轮** | 系统持续录音，持续识别，自动判断新问题，无需手动操作 |
| **面试过程中回答被误识别为问题** | 提供“标记为非问题”的交互按钮，用户可手动纠错 |
| **网络断开怎么办** | 前端检测网络状态，断开时提示用户检查网络；已生成的回答保留在本地 |
| **多次调用大模型的成本** | 在设置中提供“每次面试最大调用次数”限制，超出后提示用户 |
| **面试记录如何保存** | 提供“导出对话记录”功能（JSON/TXT/Markdown格式），方便用户复盘 |
| **知识库更新滞后** | 在配置页面显示知识库状态（就绪/解析中/不可用），并提示用户等待 |
| **多轮对话的上下文** | 在Prompt中自动携带最近2轮对话历史，保持回答的连贯性 |
| **ASR密钥如何配置** | ASR_TOKEN和ASR_APP_ID在后端`.env`中配置，不提交Git；未配置时自动降级到浏览器Web Speech API |
| **ASR成本控制** | 火山引擎ASR按音频时长计费（约0.03元/分钟），面试30分钟约0.9元；支持并发版固定计费 |


## 附录

### A. 火山引擎相关文档

- 火山方舟大模型平台：[https://www.volcengine.com/docs/82379](https://www.volcengine.com/docs/82379)
- 文本生成 Chat API：[https://www.volcengine.com/docs/82379/1399009](https://www.volcengine.com/docs/82379/1399009)
- 企业知识引擎API：[https://www.volcengine.com/docs/86760/1869536](https://www.volcengine.com/docs/86760/1869536)
- **豆包语音 · 大模型流式语音识别**：[https://www.volcengine.com/docs/6561/1354869](https://www.volcengine.com/docs/6561/1354869)
- **语音识别计费说明**：[https://www.volcengine.com/docs/6561/1359370](https://www.volcengine.com/docs/6561/1359370)

### B. 浏览器API参考

- MediaStream Recording API：[https://developer.mozilla.org/zh-CN/docs/Web/API/MediaStream_Recording_API](https://developer.mozilla.org/zh-CN/docs/Web/API/MediaStream_Recording_API)
- Web Speech API：[https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- Web Audio API (AudioContext)：[https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)