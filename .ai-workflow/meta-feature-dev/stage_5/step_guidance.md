# Stage 5: 分步指导

## 实施步骤（按依赖顺序）

### Step 1: 配置层
**文件**: `backend/config.py`
**改动**: 第 22 行后新增 2 行
```python
LOCAL_KB_ORIGINALS_DIR = os.getenv("LOCAL_KB_ORIGINALS_DIR",
    os.path.join(LOCAL_KB_DATA_DIR, "originals"))
```
**验收**: `from config import LOCAL_KB_ORIGINALS_DIR` 可正常导入
**依赖**: 无

### Step 2: 核心持久化
**文件**: `backend/app/services/local_knowledge.py`
**改动**: 
- 顶部新增 `import shutil` 和 `from config import LOCAL_KB_ORIGINALS_DIR`
- `upload()` 第 170-172 行 finally 块 → 复制原文件
- `list_docs()` 第 208-212 行 → 追加 `file_size_bytes`
- `delete_doc()` 第 239-249 行 → 同步删除原文件
- `clear()` 第 264-265 行 → 同步清空原文件
**验收**: 
- 上传 PDF → `data/chroma/originals/` 下有对应文件
- `GET /api/local_kb/list` 返回含 `file_size_bytes`
- 删除文档 → 原文件同步删除
- 清空 → originals/ 目录清空
**依赖**: Step 1

### Step 3: .env 模板 + .gitignore
**文件**: `backend/.env.example`, `.gitignore`
**改动**: 各加 1 行注释
**验收**: 新用户能看到配置说明，originals/ 不入库
**依赖**: 无（可并行）

### Step 4: 下载 API
**文件**: `backend/app/routes/local_kb.py`
**改动**: 
- 新增 `from fastapi.responses import FileResponse` 和 `from config import LOCAL_KB_ORIGINALS_DIR`
- 第 155 行后新增 `download_document` 端点
**验收**: `GET /api/local_kb/download/{doc_id}` 返回原文件
**依赖**: Step 1（需要 LOCAL_KB_ORIGINALS_DIR）

### Step 5: 前端下载按钮
**文件**: `frontend/src/components/ConfigModal.vue`
**改动**: 
- 新增 `Download` 图标从 lucide-vue-next 导入
- 文档列表每项增加下载按钮 + `downloadDoc()` 方法
**验收**: 点击下载按钮，浏览器下载原文件
**依赖**: Step 4

## 依赖关系图

```
Step 1 (config) ──→ Step 2 (core logic) ──→ Step 4 (API) ──→ Step 5 (frontend)
                                          ↘
                    Step 3 (.env + .gitignore) ← 可并行
```

## 验收标准（总）

1. ✅ 上传 PDF/TXT/MD/DOCX/JSON → originals/ 目录有对应文件
2. ✅ 下载按钮可下载原文件，文件名正确
3. ✅ 删除文档时原文件同步删除
4. ✅ 清空知识库时 originals/ 目录清空
5. ✅ `.gitignore` 排除 originals/
6. ✅ 无 lint 错误
7. ✅ 不影响现有功能（上传/检索/列表/统计）

## 门控状态
- [x] steps_decomposed — 5 步
- [x] acceptance_criteria_per_step — 每步有验收标准
- [x] dependency_order_defined — 依赖图已绘制
