# curl 测试命令 — RAG 3.0 升级验证

**Base URL**: `http://localhost:8001`
**来源**: `question.py:62-176`, `main.py:86-88`, `local_knowledge.py:157-223`

---

## 1. 健康检查

来源: `health.py:7`, `main.py:83`

```bash
curl -s http://localhost:8001/api/health | python3 -m json.tool
```

---

## 2. POST /api/question（非流式）

来源: `question.py:62-116`

### 基础问答（本地知识库）
```bash
curl -X POST http://localhost:8001/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是微服务架构？",
    "kb_provider": "local",
    "stream": false,
    "session_id": "test-curl-001"
  }'
```

### RAG3 混合检索 + 多轮记忆
```bash
# 第一轮
curl -X POST http://localhost:8001/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "请介绍一下微服务的优缺点",
    "kb_provider": "local",
    "stream": false,
    "session_id": "test-curl-001"
  }'

# 跟进问题（期望命中 P2 SessionMemory 缓存）
curl -X POST http://localhost:8001/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "那具体怎么落地呢？",
    "kb_provider": "local",
    "stream": false,
    "session_id": "test-curl-001"
  }'
```

### 火山引擎知识库（默认）
```bash
curl -X POST http://localhost:8001/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "微服务架构有什么优缺点？",
    "stream": false
  }'
```

---

## 3. POST /api/question/stream（SSE 流式）

来源: `question.py:119-176`

```bash
curl -X POST http://localhost:8001/api/question/stream \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "question": "什么是微服务？",
    "kb_provider": "local",
    "session_id": "test-curl-stream"
  }'
```

---

## 4. 参数校验

来源: `question.py:17` min_length=1

```bash
# 空问题 — 期望 422
curl -s -X POST http://localhost:8001/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "",
    "kb_provider": "local",
    "stream": false
  }' | python3 -m json.tool
```

---

## 5. 查看 Docker 日志（RAG3 模块初始化）

```bash
docker logs interview-tiger-backend 2>&1 | grep -E "\[RAG3\]|\[Hybrid\]|\[Memory\]|\[Validator\]|\[Rewriter\]"
```
