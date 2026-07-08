# Stage 2: 方案设计

## 机械臂产出数据
- **find_similar**: 项目中无类似文件持久化模式
- **scan_imports(等价)**: `local_knowledge.py` 被 `kb_provider.py` 工厂引用 → `local_kb.py` 路由使用，无其他调用者

## 方案对比

### 方案 A：扩展 LocalKnowledgeProvider（推荐 ✅）

**做法**：在 `upload()` 中改用 `shutil.copy2` 替代 `os.remove`，在 `delete_doc()`/`clear()` 中追加文件清理

**优点**：
- 改动集中在 1 个文件，影响面最小
- 借用已有 `data_dir` 路径体系
- 不改变现有 API 契约

**缺点**：
- 存储和向量混在同一个 `data_dir` 下（通过 `originals/` 子目录隔离）

### 方案 B：独立的 LocalFileManager 类

**做法**：新建 `backend/app/services/file_manager.py`，`upload()`/`delete_doc()`/`clear()` 解耦文件管理

**优点**：
- 职责分离，SRP
- 便于后续扩展（如文件预览、版本管理）

**缺点**：
- 新增文件 + 依赖注入，改动面更大
- 当前需求简单，过度设计

### 方案 C：PostgreSQL BYTEA 存储

**做法**：原文件存入 PostgreSQL 的 BYTEA 字段

**优点**：
- 与数据库一体备份
- 支持事务

**缺点**：
- 大文件存入数据库性能差
- 当前 PostgreSQL 仅用于潜在扩展，非核心依赖
- 过度设计

## 推荐方案

✅ **方案 A**，理由：
1. 改动集中在 `local_knowledge.py` 的 3 个方法，6 文件总计约 60 行新增
2. 零架构变更，零新依赖
3. 满足 R01-R04 全部需求
4. 后续可演进到方案 B（文件管理逻辑已在 Provider 内，提取即可）

## 可选抉择

| 决策点 | 选项 | 推荐 | 理由 |
|---|---|---|---|
| 存储位置 | `data_dir/originals/` | ✅ | 与向量同目录便于备份 |
| 文件命名 | `{doc_id}_{filename}` | ✅ | 避免同名冲突，可知文件名 |
| list_docs 增强 | 追加 `file_size_bytes` | ✅ | 前端可展示文件体积 |
| 下载端点 | `GET /api/local_kb/download/{doc_id}` | ✅ | RESTful |

## 门控状态
- [x] alternatives_listed — 3 个方案已列出
- [x] recommendation_made — 方案 A
- [x] tradeoffs_documented — 优劣已对比
