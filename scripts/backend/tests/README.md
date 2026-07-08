# 面试虎 - 本地知识库接口测试

## 概述

对本地知识库（local_kb）全部 7 个接口进行真实业务流程测试，使用真实的面试知识库文件。

## 测试流程

| 场景 | 内容 | 涉及接口 |
|------|------|----------|
| S1 | 健康检查 + 初始状态基线 | /api/health, /api/local_kb/stats, /api/local_kb/list |
| S2 | 上传真实面试知识库文件 | /api/local_kb/upload |
| S3 | 验证上传结果（列表/搜索/下载/统计） | /api/local_kb/list, /api/local_kb/search, /api/local_kb/download/{doc_id}, /api/local_kb/stats |
| S4 | 清理（删除+清空+验证） | /api/local_kb/delete/{doc_id}, /api/local_kb/list, /api/local_kb/download/{doc_id}, /api/local_kb/clear, /api/local_kb/stats |

## 运行方式

### 一键运行（推荐）

```bash
# 完整测试（含清理）
./run_all.sh

# 仅 P0 测试（上传 + 验证，保留数据）
./run_p0.sh
```

### 手动运行

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| TEST_BASE_URL | 后端服务地址 | http://localhost:8001 |
| TEST_FILE_PATH | 测试用文件路径 | ~/Documents/个人信息/.../01-自我介绍与核心必答题.md |
| TEST_TIMEOUT | 请求超时（秒） | 120 |

## 前置条件

- 后端服务已启动（端口 8001）
- KB_PROVIDER=local（已在 .env 中配置）
- ChromaDB 和 Embedding 模型已初始化
