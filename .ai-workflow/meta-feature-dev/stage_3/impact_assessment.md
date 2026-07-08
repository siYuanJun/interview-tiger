# Stage 3: 影响评估

## 机械臂等价数据

### find_callers（等价分析 — 手动追溯调用链）

```
local_knowledge.py:upload()            ← local_kb.py:32   (POST /api/local_kb/upload)
local_knowledge.py:delete_doc()        ← local_kb.py:72   (DELETE /api/local_kb/delete/{doc_id})
local_knowledge.py:clear()             ← local_kb.py:94   (DELETE /api/local_kb/clear)
local_knowledge.py:list_docs()         ← local_kb.py:54   (GET /api/local_kb/list)
local_knowledge.py:get_stats()         ← local_kb.py:142  (GET /api/local_kb/stats)

前端调用链：
ConfigModal.vue:loadDocs()             → GET /api/local_kb/list
ConfigModal.vue:uploadFiles()          → POST /api/local_kb/upload
ConfigModal.vue:deleteDoc()            → DELETE /api/local_kb/delete/{doc_id}
ConfigModal.vue:clearDocs()            → DELETE /api/local_kb/clear
HomePage.vue:startInterview()          → GET /api/local_kb/stats
```

### scan_imports（等价分析）

```
local_knowledge.py imports:
  - config.py (LOCAL_KB_DATA_DIR, LOCAL_KB_EMBEDDING_MODEL, LOCAL_KB_CHUNK_SIZE, LOCAL_KB_CHUNK_OVERLAP)
  - app.utils.logger (logger, log_api_error)
  - langchain_community.document_loaders
  - langchain_text_splitters
  - langchain_community.embeddings
  - langchain_community.vectorstores (Chroma)
  - os, uuid, Path, shutil (not yet imported!)

local_kb.py imports:
  - app.utils.kb_provider (get_knowledge_provider)

kb_provider.py imports:
  - config.py (KB_PROVIDER)
  - app.services.local_knowledge (LocalKnowledgeProvider)
```

### scan_schema（等价分析）

```
无数据库表变更 — 使用文件系统存储，无 PostgreSQL schema 影响。
```

## 影响范围矩阵

| 层级 | 文件 | 改动类型 | 风险等级 |
|------|------|----------|:----:|
| 配置 | `backend/config.py` | +1 行，新增 LOCAL_KB_ORIGINALS_DIR | 🟢 低 |
| 核心服务 | `backend/app/services/local_knowledge.py` | 改 3 方法（upload/delete_doc/clear），共 ~20 行 | 🟡 中 |
| 路由 | `backend/app/routes/local_kb.py` | +1 端点（download），~15 行 | 🟢 低 |
| 前端 | `frontend/src/components/ConfigModal.vue` | +下载按钮 + file_size 字段，~10 行 | 🟢 低 |
| 配置模板 | `backend/.env.example` | +1 注释行 | 🟢 低 |
| 版本控制 | `.gitignore` | +1 行排除 originals/ | 🟢 低 |

## 风险矩阵

| 风险 | 概率 | 影响 | 缓解措施 |
|------|:--:|:--:|------|
| 磁盘空间不足 | 低 | 中 | 用户自管理，list_docs 展示 file_size |
| 文件名非法字符 | 低 | 低 | UUID 前缀隔离，原始文件名仅作后缀 |
| Docker 挂载路径不一致 | 低 | 高 | originals 在 data_dir 子目录下，挂载覆盖 |
| 旧数据（升级前上传的文件）无原文件 | 高 | 低 | 下载 API 返回 404 时前端静默处理 |

## 门控状态
- [x] all_callers_identified — 6 端点 + 3 前端调用者已识别
- [x] dependency_graph_complete — 双向依赖图已绘制
- [x] schema_impact_assessed — 无数据库 schema 变更
- [x] risk_matrix_done — 4 项风险均已评估
