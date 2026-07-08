# Stage 7: 测试与文档

## 回归测试

### 测试1：上传文件 → 原始文件持久化 ✅
```bash
# 上传测试文件
curl -X POST http://localhost:8000/api/local_kb/upload \
  -F "files=@test.txt" \
  -F "chunk_size=500" -F "chunk_overlap=50"

# 验证原文件存在
ls backend/data/chroma/originals/
# 预期：{doc_id}_test.txt 存在
```

### 测试2：列表 API 返回 file_size_bytes ✅
```bash
curl http://localhost:8000/api/local_kb/list
# 预期：data[0].file_size_bytes > 0
```

### 测试3：下载原文件 ✅
```bash
curl -O http://localhost:8000/api/local_kb/download/{doc_id}
# 预期：Content-Disposition: attachment，文件与上传一致
```

### 测试4：删除文档 → 同步删除原文件 ✅
```bash
curl -X DELETE http://localhost:8000/api/local_kb/delete/{doc_id}
# 验证：originals/ 目录下对应文件已被删除
```

### 测试5：清空知识库 → 同步清空原文件 ✅
```bash
curl -X DELETE http://localhost:8000/api/local_kb/clear
# 验证：originals/ 目录为空（目录本身保留）
```

### 测试6：下载不存在的文件 → 404 ✅
```bash
curl http://localhost:8000/api/local_kb/download/nonexistent-id
# 预期：404
```

### 测试7：前端下载按钮可见 ✅
- 打开应用 → 设置 → 本地知识库 → 文档列表
- 预期：每项显示 下载 + 删除 + 文件大小

## 文档更新

- [x] `.env.example` — 新增 LOCAL_KB_ORIGINALS_DIR 配置说明
- [x] STAGES 1-6 完整记录在 `.ai-workflow/meta-feature-dev/`

## 变更日志

### 模块10：本地知识库原始文件持久化

| 文件 | 变更 |
|---|---|
| `backend/config.py` | +3 行：新增 `LOCAL_KB_ORIGINALS_DIR` 配置 |
| `backend/.env.example` | +3 行：配置说明注释 |
| `backend/app/services/local_knowledge.py` | +20 行：upload/delete_doc/clear 增加原文件管理 + list_docs 增加 file_size_bytes |
| `backend/app/routes/local_kb.py` | +25 行：新增 `GET /api/local_kb/download/{doc_id}` 下载端点 |
| `frontend/src/components/ConfigModal.vue` | +12 行：Download 图标 + downloadDoc 方法 + 下载按钮 + file_size 展示 |
| `.gitignore` | +2 行：排除 originals/ 目录 |

**总计**：6 文件，约 65 行新增，零删除，零架构变更，零 lint 错误。
