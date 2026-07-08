# 🐯 面试虎 — 部署指南

> Docker Compose 一键部署

## 📋 前置条件

- **Docker 20.10+**
- **Docker Compose 2.0+**
- **至少 4GB 内存**（用于运行本地知识库 Embedding 模型）

## 🚀 快速部署

```bash
# 进入项目目录
cd interview-tiger

# 构建并启动所有服务
docker-compose up --build -d

# 服务启动后访问：
# - 前端页面：http://localhost:40003
# - 后端 API：http://localhost:8001
```

## 🔧 环境变量配置

创建 `.env` 文件（可选，也可在前端页面配置）：

```bash
cp .env.example .env
```

### 后端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ARK_API_KEY` | - | 火山引擎方舟平台 API Key |
| `ARK_MODEL_ID` | `deepseek-v4-flash-260425` | 大模型 ID |
| `ARK_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | 大模型 API 地址 |
| `KB_PROVIDER` | `volcengine` | 知识库提供者：`volcengine` 或 `local` |
| `KB_ID` | `siyuan_jianli` | 火山引擎知识库 ID |
| `KB_API_KEY` | - | 火山引擎知识库 API Key |
| `KB_PROJECT` | `default` | 火山引擎知识库项目名 |
| `KB_BASE_URL` | `https://api-knowledgebase.mlp.cn-beijing.volces.com` | 知识库 API 地址 |
| `LOCAL_KB_DATA_DIR` | `./data/chroma` | 本地知识库数据目录 |
| `LOCAL_KB_EMBEDDING_MODEL` | `bge-large-zh-v1.5` | 本地 Embedding 模型 |
| `LOCAL_KB_CHUNK_SIZE` | `500` | 默认切片大小 |
| `LOCAL_KB_CHUNK_OVERLAP` | `50` | 默认切片重叠 |
| `POSTGRES_HOST` | `db` | 数据库主机 |
| `POSTGRES_PORT` | `5432` | 数据库端口 |
| `POSTGRES_USER` | `interview` | 数据库用户名 |
| `POSTGRES_PASSWORD` | `tiger123` | 数据库密码 |
| `POSTGRES_DB` | `interview_tiger` | 数据库名 |

## 🐳 Docker Compose 服务说明

```yaml
services:
  backend:    # 后端 API 服务
    ports:
      - "8001:8000"
    depends_on:
      - db
  
  frontend:   # 前端页面
    ports:
      - "40003:40003"
  
  db:         # PostgreSQL 数据库
    ports:
      - "5432:5432"
```

## 📊 服务状态检查

```bash
# 查看所有服务状态
docker-compose ps

# 查看后端日志
docker logs interview-tiger-backend -f

# 查看前端日志
docker logs interview-tiger-frontend -f

# 检查后端健康状态
curl http://localhost:8001/api/health
```

## 🔄 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重新构建并重启（修改代码后）
docker-compose up --build -d
```

## 🛑 停止服务

```bash
# 停止服务（保留数据）
docker-compose down

# 停止服务并删除数据卷（谨慎使用）
docker-compose down -v
```

## ⚠️ 常见问题

### 问题 1：构建缓慢 / 网络超时

确保 Docker Desktop 已配置国内镜像源：

```json
// Docker Engine 配置
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://hub-mirror.c.163.com"
  ]
}
```

### 问题 2：内存不足

本地知识库使用 BGE-Large-ZH-v1.5 模型，建议分配至少 4GB 内存给 Docker。

### 问题 3：端口冲突

修改 `docker-compose.yml` 中的端口映射：

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # 修改为未占用的端口
  
  frontend:
    ports:
      - "8081:40003"  # 修改为未占用的端口
```