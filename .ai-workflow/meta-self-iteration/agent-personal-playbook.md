# Agent Personal Playbook — 面试虎项目

## 一、问题处理经验总结

### 1. 踩坑记录与最终解法

#### 问题类型：知识库 API 认证失败（HTTP 403）

**排查思路**：
1. 检查 API Key 是否配置正确
2. 检查请求头格式（Bearer Token vs SignerV4）
3. 验证 API Key 类型是否匹配服务端要求

**最终有效解法**：
- KB_API_KEY 必须使用 OpenViking Service 控制台获取的 VIKING_API_KEY（sk-xxx 格式）
- 不能使用 AK:SK 格式的密钥（SignerV4 认证不适用于知识库 API）
- 配置位置：backend/.env 文件中的 KB_API_KEY

**失败的尝试 + 教训**：
- 添加 KB_ACCOUNT_ID 到 .env（无效，因为知识库 API 使用 Bearer Token 认证）
- 使用 AK:SK 格式密钥（导致 403 签名错误）

**适用边界**：仅适用 OpenViking 知识库 API，不适用需要 SignerV4 认证的其他 API

**验证依据**：session_delta.json 会话3 — "HTTP 403 signature errors due to missing 'V-Account-Id' header"、"KB_API_KEY was in AK:SK format (for SignerV4) instead of the required Bearer Token format (sk-xxx)"

---

#### 问题类型：API Key 配置不生效

**排查思路**：
1. 确认前端请求参数是否传递
2. 检查后端路由是否正确读取 .env 作为默认值
3. 验证 resolve_config() 函数逻辑

**最终有效解法**：
- 在路由层实现 `resolve_config()` 函数处理默认值回退
- 优先级：前端请求参数 > .env 配置 > 默认空值
- 确保所有 API Key 参数（ark_api_key, kb_api_key）能动态传递

**失败的尝试 + 教训**：
- 直接使用 .env 值而不支持前端参数覆盖（不够灵活）

**适用边界**：所有需要 API Key 的后端服务

**验证依据**：session_delta.json 会话1 — "API Key configuration priority: frontend request parameters > .env configuration > default empty value"、"ARK_API_KEY, KB_ID, KB_API_KEY which serve as default values when frontend parameters are not provided"

---

### 2. 通用问题排查方法论

**接口报错排查模板**：
1. 先看日志定位异常类型（docker logs / app.log）
2. 确认请求参数是否正确传递
3. 追踪调用链定位问题代码（Controller→Service→Dao）
4. 修复 + 验证

**容器异常排查模板**：
1. docker ps 确认容器状态
2. docker logs 查看错误日志
3. docker inspect 检查配置
4. 根据日志信息修复

**验证依据**：基于所有会话中问题排查模式的归纳总结

---

## 二、工作与技术偏好档案

### 1. 开发与编码偏好

- **代码风格**：使用统一的日志模块（app/utils/logger.py），日志包含短日志和长日志
- **技术选择**：
  - 后端：Python FastAPI + Uvicorn
  - 数据库：PostgreSQL（Docker 容器）
  - 容器化：Docker Compose
  - 日志格式：[log_type].[date].log（如 app.2026-07-07.log）

**验证依据**：session_delta.json 会话1 — "PostgreSQL must be started via Docker container"、"Logs must include both short logs and long logs"；会话2、3、4 — 技术栈关键词（python, vue, docker, postgres, api）

### 2. 沟通与协作偏好

- **回复要求**：回复使用中文，称呼用户为"老板"，自称"小t"
- **任务处理**：复杂任务先规划 TodoList，分步执行

**验证依据**：用户 profile 和项目记忆中明确的沟通规则

### 3. 风险与边界偏好

- **直接拒绝的方案**：跳过测试直接上线、不检查代码就执行命令
- **必须规避的坑**：API Key 格式错误（AK:SK 不能用于 OpenViking）
- **不能碰的红线**：明文存储密码、提交真实密钥到版本控制

**验证依据**：session_delta.json 会话3 — KB_API_KEY 格式错误导致认证失败；安全扫描记录

---

## 三、可复用规则清单

⚠️ 前置元规则：防止固化偏见

本手册所有经验在下一次使用时，必须先过三道闸门：

闸门 1：症状真的相同吗？
  → 不只看表面现象（如 404/500），还要对比报错细节、触发条件、环境上下文

闸门 2：环境变化了吗？
  → 服务是否迁移？依赖版本是否升级？部署模式是否变化？

闸门 3：有没有更简单的方案？
  → 手册里的是历史解法，不代表当前最优解。优先考虑原生配置/工具链修复而非手动 hack

如果任一闸门触发"不完全匹配"，手册规则仅作参考，必须优先从头分析当前上下文。

---

### 问题排查规则
- 遇到知识库 API 403 → 优先检查 KB_API_KEY 格式（sk-xxx vs AK:SK）
- 遇到 API Key 不生效 → 优先检查 resolve_config() 回退逻辑

### 代码/脚本规范
- 异常必须记录日志
- API Key 参数必须支持前端传递和 .env 默认值
- 日志文件必须使用 [log_type].[date].log 格式

### 沟通格式
- 修复方案必须附带验证命令
- 任务进度使用 TodoList 跟踪

### 默认工具选择
- 排查容器问题 → docker ps + docker logs + docker inspect
- 排查 API 问题 → curl + 日志分析

### 绝对红线
- 不提交真实密钥到版本控制
- 不使用 AK:SK 格式密钥访问 OpenViking 知识库 API
- 不跳过测试直接上线

---

## 维护说明

- 当规则被证明不适用时，必须**补充边界条件**而非删除规则
- 每月至少检查一次是否存在因盲目套用历史规则导致绕路的情况
- 跨项目使用时，先做反固化三闸门校验
- 新场景出现时，先追加「适用边界」再使用

---

**生成信息**：
- 版本：v1.0.0
- 生成时间：2026-07-07
- 数据来源：4 个会话（29221 字符）
- 验证状态：✅ 2 个问题模式已验证，⚠️ 2 个模式因证据不足已移除