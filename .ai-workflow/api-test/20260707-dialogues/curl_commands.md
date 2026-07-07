# curl 测试命令

## 测试: GET /api/dialogues
来源: transcript.py:87

### 按 session_id 查询
```bash
curl -X GET "http://localhost:40003/api/dialogues?session_id=session_1783434223843_ynl6rb59b"
```

### 查询所有对话（不传 session_id）
```bash
curl -X GET "http://localhost:40003/api/dialogues"
```

### 直接测试后端（绕过前端代理）
```bash
curl -X GET "http://localhost:8001/api/dialogues?session_id=session_1783434223843_ynl6rb59b"
```
