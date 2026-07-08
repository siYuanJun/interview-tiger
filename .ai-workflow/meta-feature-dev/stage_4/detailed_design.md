# Stage 4: 详细设计

## 架构变更

```
原架构：
  upload() → /tmp/ → 文本提取 → ChormaDB → os.remove(temp_path)

新架构：
  upload() → /tmp/ → 文本提取 → ChormaDB → shutil.copy2(→ originals/) → os.remove(temp_path)
  delete_doc() → ChormaDB delete → originals/*unlink()
  clear() → ChormaDB clear → rmtree(originals/)
  download → GET /api/local_kb/download/{doc_id} → FileResponse
```

## 数据模型

### originals/ 目录结构
```
data/chroma/
├── originals/                    # 新增
│   ├── {doc_id}_简历.pdf
│   ├── {doc_id}_项目介绍.txt
│   └── ...
└── chroma.sqlite3               # 已有（ChromaDB 索引）
```

### 文件命名规则
- 格式：`{doc_id}_{original_filename}`
- doc_id：upload() 中 `uuid.uuid4()` 生成的唯一标识
- 好处：通过 `glob(f"{doc_id}_*")` 快速定位

## 接口定义

### 1. 修改：GET /api/local_kb/list

**响应新增字段**：
```json
{
  "code": 0,
  "data": [
    {
      "doc_name": "简历.pdf",
      "doc_id": "abc123",
      "chunks": 15,
      "file_size_bytes": 204800   // 新增
    }
  ]
}
```

### 2. 新增：GET /api/local_kb/download/{doc_id}

**请求**：`GET /api/local_kb/download/{doc_id}`
**成功**：返回文件流，Content-Disposition: attachment
**失败**：404 `{"code": -1, "message": "原始文件不存在"}`
**内容类型**：自动推断（application/pdf, text/plain 等）

## 代码级设计

### config.py 变更
```python
# 新增 1 行（第 22 行后）
LOCAL_KB_ORIGINALS_DIR = os.getenv("LOCAL_KB_ORIGINALS_DIR",
    os.path.join(LOCAL_KB_DATA_DIR, "originals"))
```

### local_knowledge.py 变更

**upload() 方法（第 170-172 行）替换 finally 块**：
```python
finally:
    # 持久化原始文件
    originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
    originals_dir.mkdir(parents=True, exist_ok=True)
    if docs:
        doc_id = docs[0].metadata['doc_id']
        persistent_path = originals_dir / f"{doc_id}_{file.filename}"
        import shutil
        shutil.copy2(temp_path, persistent_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)
```

**list_docs() 方法（第 192-218 行）追加 file_size**：
```python
# 在 doc_map[source] 初始化时追加
doc_map[source] = {
    "doc_name": source,
    "doc_id": metadata.get('doc_id', ''),
    "chunks": 0,
    "file_size_bytes": metadata.get('file_size', 0)  # 新增
}
```

**delete_doc() 方法（第 238-249 行）追加原文件删除**：
```python
if ids_to_delete:
    collection.delete(ids=ids_to_delete)
    self._vector_store.persist()
    # 同步删除原始文件
    originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
    for f in originals_dir.glob(f"{doc_id}_*"):
        f.unlink()
    return {...}
```

**clear() 方法（第 264-265 行）追加原文件清空**：
```python
collection.delete(ids=results.get('ids', []))
self._vector_store.persist()
# 清空原始文件
originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
if originals_dir.exists():
    shutil.rmtree(originals_dir)
    originals_dir.mkdir(parents=True, exist_ok=True)
```

### local_kb.py 新增下载端点（第 155 行后）
```python
from fastapi.responses import FileResponse
from config import LOCAL_KB_ORIGINALS_DIR

@router.get("/local_kb/download/{doc_id}")
async def download_document(doc_id: str):
    originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
    matches = list(originals_dir.glob(f"{doc_id}_*"))
    if not matches:
        raise HTTPException(status_code=404, detail="原始文件不存在")
    
    file_path = matches[0]
    original_name = file_path.name[len(doc_id) + 1:]
    
    # 推断 MIME 类型
    ext = file_path.suffix.lower()
    mime_map = {".pdf": "application/pdf", ".txt": "text/plain",
                ".md": "text/markdown", ".json": "application/json",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    media_type = mime_map.get(ext, "application/octet-stream")
    
    return FileResponse(file_path, filename=original_name, media_type=media_type)
```

### ConfigModal.vue 变更
在文档列表每项 `<div>` 中增加下载按钮（第 421 行旁）：
```html
<button @click.stop="downloadDoc(doc.doc_id)"
  class="p-2 rounded-lg hover:bg-blue-500/10 text-foreground/40 hover:text-blue-400 transition-all">
  <Download class="w-4 h-4" />
</button>
```

新增方法：
```typescript
function downloadDoc(docId: string) {
  window.open(`/api/local_kb/download/${docId}`, '_blank')
}
```

## 门控状态
- [x] architecture_documented
- [x] data_model_designed
- [x] interface_defined
