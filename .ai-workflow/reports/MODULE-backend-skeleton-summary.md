# 后端项目骨架模块 - 模块摘要

## 📌 一句话概括

面试虎的后端基础架构，提供FastAPI服务框架、路由注册、全局异常处理和配置管理，支持API接口开发和外部服务调用。

---

## 👤 面向产品/业务人员

### 这个模块做了什么？

后端项目骨架是面试虎应用的"大脑"，负责处理前端发来的请求，调用外部服务（知识库、大模型），并返回结果。它搭建了Python FastAPI框架，创建了健康检查、配置管理、知识库检索、大模型调用等API接口，确保前后端能够正常通信。

### 用户可以做什么？

| 用户故事 | 操作路径 | 完成状态 |
|---------|---------|----------|
| 检查服务是否正常运行 | 访问 /api/health | ✅ |
| 保存API配置 | 调用 POST /api/config | ✅ |
| 获取当前配置 | 调用 GET /api/config | ✅ |
| 检索知识库 | 调用 POST /api/search | ✅ |
| 生成AI回答 | 调用 POST /api/generate | ✅ |

### 涉及几个页面？

此模块为后端服务，不直接涉及页面。

---

## 🔧 面向技术负责人

### 涉及接口清单

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/health | 健康检查 |
| GET | /api/config | 获取配置（脱敏） |
| POST | /api/config | 保存配置 |
| POST | /api/search | 知识库检索 |
| POST | /api/generate | 大模型调用（非流式） |
| POST | /api/generate/stream | 大模型调用（流式） |
| POST | /api/question | 问题处理（非流式） |
| POST | /api/question/stream | 问题处理（流式） |

### 关键数据结构

```
QuestionRequest (Pydantic模型)
├── question: str            # 面试问题
├── ark_api_key: str         # 火山引擎API Key
├── kb_id: str               # 知识库ID
├── kb_api_key: str          # 知识库API Key
├── model_id: str            # 模型ID
├── temperature: float       # 温度参数
└── max_tokens: int          # 最大token数

统一响应格式
├── code: int                # 状态码
├── message: str             # 消息
└── data: dict               # 数据
```

### 关键架构决策

| ADR编号 | 决策内容 | 影响面 |
|---------|---------|--------|
| ADR-004 | 选择FastAPI作为后端框架 | 整个后端项目 |

### 风险与注意事项

| 风险项 | 级别 | 说明 | 缓解措施 |
|--------|------|------|----------|
| 无请求限流 | 🟡中 | 高频请求可能导致服务过载 | 建议添加限流中间件 |
| 无数据库持久化 | 🟡中 | 配置和对话仅存储在内存 | 建议后续添加数据库 |

---

## ✅ 模块验收状态

| 验收项 | 状态 | 备注 |
|--------|------|------|
| 功能完整性 | ✅ | 所有API路由注册成功 |
| 测试覆盖率 | ✅ | 配置接口测试通过(4/4) |
| 文档完成度 | ✅ | 流程+设计+摘要+检查清单 |
| 代码规范 | ✅ | RESTful + 统一响应格式 |

---

## 📎 相关文档

- [模块流程图](./MODULE-backend-skeleton-flow.md)
- [模块设计说明](./MODULE-backend-skeleton-design.md)
- [模块测试报告](./MODULE-backend-skeleton-test-report.md)
- [模块验收检查清单](./MODULE-backend-skeleton-checklist.md)