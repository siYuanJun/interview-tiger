# 实时语音识别模块 - 验收检查清单

## 功能检查

### 语音识别功能

- [ ] 麦克风权限请求正常
- [ ] 语音识别服务启动正常
- [ ] interim结果实时返回
- [ ] final结果正确合并
- [ ] 识别错误提示友好

### 实时显示功能

- [ ] interim结果实时显示在左侧面板
- [ ] 文本颜色区分已确认/未确认状态
- [ ] 2秒停顿后自动确认当前消息
- [ ] 手动"完成"按钮可强制结束
- [ ] 新消息自动滚动到可视区域

### 左右布局

- [ ] 左侧显示用户消息（深蓝色气泡）
- [ ] 右侧显示AI回答（毛玻璃气泡）
- [ ] 流式回答有打字机效果
- [ ] 回答加载状态有动画提示

### 自动调用大模型

- [ ] 消息确认后自动调用大模型
- [ ] 知识库检索正常
- [ ] 大模型回答流式返回
- [ ] 回答完成后保存到数据库

## 架构检查

### 前端架构

- [ ] useSpeech.ts 新增 pauseTimer 变量
- [ ] useSpeech.ts 新增 resetPauseTimer 方法
- [ ] useSession.ts 新建，管理 session_id
- [ ] useApi.ts 新增 createDialogue 方法
- [ ] useApi.ts 新增 updateDialogue 方法
- [ ] InterviewPage.vue 左右布局实现
- [ ] InterviewPage.vue 实时显示逻辑

### 后端架构

- [ ] requirements.txt 添加 SQLAlchemy 和 psycopg2
- [ ] config.py 添加 DATABASE_URL 配置
- [ ] app/models.py 新建，定义 Dialogue 模型
- [ ] app/database.py 新建，数据库连接管理
- [ ] app/routes/transcript.py 更新，添加CRUD接口
- [ ] docker-compose.yml 新建，PostgreSQL容器配置

### 数据库

- [ ] dialogues 表结构正确
- [ ] session_id 索引创建
- [ ] created_at 索引创建
- [ ] 数据库迁移脚本（如有）

## 接口检查

### POST /api/dialogues

- [ ] 请求参数验证（session_id, question 必填）
- [ ] 响应格式正确（code, message, data）
- [ ] 返回完整对话记录

### GET /api/dialogues/{session_id}

- [ ] 根据session_id查询
- [ ] 返回对话列表
- [ ] 按创建时间排序

### PUT /api/dialogues/{id}

- [ ] 更新answer字段
- [ ] 更新knowledge_used字段
- [ ] 更新web_search_used字段

### DELETE /api/dialogues/{session_id}

- [ ] 删除指定会话所有记录
- [ ] 返回删除数量

### POST /api/question/stream

- [ ] SSE流式返回正常
- [ ] chunk类型正确
- [ ] done类型正确
- [ ] error类型正确

## 测试检查

### 单元测试

- [ ] useSpeech 2秒停顿检测测试
- [ ] useSession session_id生成测试
- [ ] API接口测试

### 集成测试

- [ ] 语音识别→实时显示→自动结束→调用LLM→保存回答完整流程
- [ ] 手动完成按钮测试
- [ ] 会话持久化测试（刷新页面后数据保留）

### 边界测试

- [ ] 空语音输入处理
- [ ] 超长语音输入处理
- [ ] 网络异常处理
- [ ] 大模型调用失败处理

## 文档检查

- [ ] MODULE-realtime-speech-flow.md ✅
- [ ] MODULE-realtime-speech-design.md ✅
- [ ] MODULE-realtime-speech-summary.md ✅
- [ ] MODULE-realtime-speech-checklist.md ✅
- [ ] MODULE-realtime-speech-test-report.md（待生成）

## 性能检查

- [ ] 语音识别延迟 < 100ms
- [ ] 2秒停顿检测准确
- [ ] 大模型流式回答无卡顿
- [ ] 数据库查询响应 < 100ms

## 安全检查

- [ ] SQL注入防护（使用ORM）
- [ ] 输入参数验证
- [ ] CORS配置正确
- [ ] API Key安全传输

## 用户体验检查

- [ ] 语音识别状态指示器清晰
- [ ] 错误提示友好
- [ ] 按钮交互反馈明显
- [ ] 响应式布局适配移动端