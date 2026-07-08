# curl 测试命令

## 测试: POST /api/question/stream
来源: backend/app/routes/question.py:113

### 正常请求（通过前端代理）

```bash
curl -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "question": "他也别想",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_api_key": "",
    "kb_provider": "volcengine",
    "stream": true
  }'
```

### 直接访问后端（跳过 Vite 代理）

```bash
curl -X POST http://localhost:8001/api/question/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "question": "他也别想",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_api_key": "",
    "kb_provider": "volcengine",
    "stream": true
  }'
```

### 缺少必填参数（参数校验）

```bash
curl -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_provider": "volcengine"
  }'
# 预期: 422 Unprocessable Entity, question 不能为空
```

### 缺少 API Key（配置校验）

```bash
curl -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "你好",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "",
    "kb_provider": "volcengine"
  }'
# 预期: 400 Bad Request, ARK_API_KEY未配置
```

### 使用本地知识库

```bash
curl -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "question": "你叫什么名字",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "",
    "kb_api_key": "",
    "kb_provider": "local",
    "stream": true
  }'
```

### 使用指定 API Key

```bash
curl -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "question": "他也别想",
    "ark_api_key": "your_ark_api_key_here",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_api_key": "your_kb_api_key_here",
    "kb_provider": "volcengine",
    "stream": true
  }'
```

### 非流式请求（stream=false）

```bash
curl -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "你好",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_provider": "volcengine",
    "stream": false
  }'
# 注：此接口始终返回 SSE，stream 参数在路由级别不影响响应格式
```

### 调试模式（详细输出）

```bash
curl -v -X POST http://localhost:40003/api/question/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "question": "他也别想",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_provider": "volcengine",
    "stream": true
  }'
```