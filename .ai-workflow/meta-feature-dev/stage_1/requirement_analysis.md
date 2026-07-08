# Stage 1: 需求澄清

## 机械臂产出数据
- **build_index**: 项目共 52 个源文件（后端 26 + 前端 26），核心改动目标 `LocalKnowledgeProvider` 类位于 `backend/app/services/local_knowledge.py`（298 行，含 8 个方法）
- **find_similar**: 项目中无 `originals` 或文件持久化相关模式，这是全新功能

## 需求确认

### 范围定义 (scope_defined ✅)
1. **retain-originals**: 上传到本地知识库的文件保留原始副本
2. **download-api**: 新增下载原文件 API 端点
3. **lifecycle-sync**: 删除/清空知识库时同步处理原文件
4. **frontend-download**: 前端文档列表增加下载按钮

### 约束条件 (constraints_listed ✅)
1. 存储位置：`LOCAL_KB_DATA_DIR/originals/`（默认 `./data/chroma/originals/`）
2. 文件命名：`{doc_id}_{原始文件名}` 避免冲突
3. 不影响现有向量化流程，仅修改 `finally` 块
4. Docker 卷挂载自动覆盖（`./backend:/app`）
5. `.gitignore` 排除 originals 目录
6. 无新增 Python 依赖（`shutil` 是标准库）

### 已有模块发现 (similar_modules_found ✅)
- `list_docs()` 返回文档列表但缺少 `file_size` 字段
- 无现成的文件下载端点
- 无现成的原文件管理逻辑

## 门控状态
- [x] scope_defined
- [x] constraints_listed
- [x] similar_modules_found
