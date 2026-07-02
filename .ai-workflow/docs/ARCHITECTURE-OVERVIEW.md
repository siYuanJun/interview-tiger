# 面试虎 - 增量架构总览

## 📋 项目信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 面试虎 - AI智能面试助手 |
| 版本 | v1.0.0 |
| 架构类型 | 前后端分离 + 外部API调用 |
| 最后更新 | 2026-07-02 |

## 🏗️ 系统架构图

```mermaid
graph TD
    subgraph 用户端
        User[用户]
        Browser[浏览器]
    end
    
    subgraph 前端应用
        HomePage[首页]
        InterviewPage[面试页面]
        ConfigModal[配置弹窗]
        DialogueItem[对话组件]
        
        useRecorder[录音Composable]
        useSpeech[语音识别Composable]
        useApi[API调用Composable]
        InterviewStore[面试状态Store]
        questionJudge[问题判断工具]
    end
    
    subgraph 后端服务
        FastAPI[FastAPI应用]
        
        subgraph Routes层
            HealthRoute[健康检查]
            ConfigRoute[配置管理]
            SearchRoute[知识库检索]
            GenerateRoute[大模型生成]
            QuestionRoute[问题处理]
            TranscriptRoute[对话记录]
        end
        
        subgraph Services层
            KnowledgeService[知识库服务]
            LLMService[大模型服务]
            PromptService[Prompt服务]
            QuestionJudgeService[问题判断服务]
        end
    end
    
    subgraph 外部服务
        VolcanoLLM[火山引擎方舟LLM]
        VolcanoKB[火山引擎知识库]
    end
    
    User --> Browser
    Browser --> HomePage
    Browser --> InterviewPage
    
    HomePage --> ConfigModal
    InterviewPage --> DialogueItem
    
    InterviewPage --> useRecorder
    InterviewPage --> useSpeech
    InterviewPage --> useApi
    InterviewPage --> InterviewStore
    
    useSpeech --> questionJudge
    
    Browser -->|HTTP请求| FastAPI
    
    FastAPI --> HealthRoute
    FastAPI --> ConfigRoute
    FastAPI --> SearchRoute
    FastAPI --> GenerateRoute
    FastAPI --> QuestionRoute
    FastAPI --> TranscriptRoute
    
    SearchRoute --> KnowledgeService
    GenerateRoute --> LLMService
    QuestionRoute --> KnowledgeService
    QuestionRoute --> PromptService
    QuestionRoute --> LLMService
    TranscriptRoute --> QuestionJudgeService
    
    KnowledgeService -->|SignerV4| VolcanoKB
    LLMService -->|Bearer Token| VolcanoLLM
    
    classDef frontend fill:#e8f5e9,stroke:#388e3c
    classDef backend fill:#fff3e0,stroke:#f57c00
    classDef external fill:#fce4ec,stroke:#c62828
    
    class HomePage,InterviewPage,ConfigModal,DialogueItem,useRecorder,useSpeech,useApi,InterviewStore,questionJudge frontend
    class FastAPI,HealthRoute,ConfigRoute,SearchRoute,GenerateRoute,QuestionRoute,TranscriptRoute,KnowledgeService,LLMService,PromptService,QuestionJudgeService backend
    class VolcanoLLM,VolcanoKB external
```

## 🔄 核心业务流程图

```mermaid
sequenceDiagram
    participant 用户
    participant 前端
    participant 后端
    participant 知识库
    participant 大模型
    
    用户->>前端: 点击开始面试
    前端->>前端: 请求麦克风权限
    前端->>前端: 开始录音和语音识别
    
    loop 持续监听
        前端->>前端: 识别到语音
        前端->>前端: 问题判断规则引擎
        alt 有效问题且不重复
            前端->>后端: POST /api/transcript (问题文本)
            后端->>后端: 保存对话记录
            
            后端->>知识库: 检索相关知识
            知识库-->>后端: 返回检索结果
            
            后端->>后端: 拼接Prompt(问题+知识)
            后端->>大模型: 调用生成接口(stream=true)
            
            loop SSE流式响应
                大模型-->>后端: 返回文本块
                后端-->>前端: SSE event: chunk
                前端->>用户: 打字机效果显示
            end
            
            大模型-->>后端: 生成完成
            后端-->>前端: SSE event: done
            前端->>用户: 显示完整回答
            
        else 无效或重复
            前端->>前端: 继续监听
        end
    end
```

## 📁 模块清单

| 模块 | 类型 | 状态 | 负责人 |
|------|------|------|--------|
| 前端项目骨架 | 前端 | ✅ 已完成 | - |
| 后端项目骨架 | 后端 | ✅ 已完成 | - |
| 录音与语音识别 | 前端 | ✅ 已完成 | - |
| 大模型调用 | 后端 | ✅ 已完成 | - |
| 知识库检索 | 后端 | ✅ 已完成 | - |
| 面试对话展示 | 前端 | ✅ 已完成 | - |

## 🌐 API接口清单

| 方法 | 端点 | 说明 | 所属模块 |
|------|------|------|----------|
| GET | /api/health | 健康检查 | 后端骨架 |
| GET | /api/config | 获取配置 | 后端骨架 |
| POST | /api/config | 保存配置 | 后端骨架 |
| POST | /api/search | 知识库检索 | 知识库检索 |
| POST | /api/generate | 大模型调用（非流式） | 大模型调用 |
| POST | /api/generate/stream | 大模型调用（流式） | 大模型调用 |
| POST | /api/question | 问题处理（非流式） | 后端骨架 |
| POST | /api/question/stream | 问题处理（流式） | 后端骨架 |
| POST | /api/transcript | 提交对话记录 | 语音识别 |
| GET | /api/dialogues | 获取对话列表 | 语音识别 |

## 📝 迭代记录

| 迭代 | 时间 | 内容 |
|------|------|------|
| v1.0.0 | 2026-07-02 | 初始版本，完成所有核心模块 |

## 🔗 相关文档

- [文档导航索引](./DOCS-INDEX.md)
- [经验知识库](./LESSONS-LEARNED.md)