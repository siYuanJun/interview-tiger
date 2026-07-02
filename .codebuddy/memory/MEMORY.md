# 面试虎项目记忆

## 项目概要
- 名称：面试虎 (interview-tiger)
- 定位：AI 智能面试助手
- 前端：Vue 3 + Vite + Pinia + TypeScript + TailwindCSS
- 后端：Python FastAPI + 火山引擎方舟大模型 + 火山引擎知识库

## 模型与知识库配置（唯一真实来源）
- **大模型**：`deepseek-v4-flash-260425`（后端 `backend/config.py`，前端 `frontend/src/constants.ts`）
- **知识库 ID**：`siyuan_jianli`
- **密钥存储**：`backend/.env`（不提交 Git），`.env.example` 为模板

## Docker 化
- 后端 Docker 启动（`docker compose up -d backend`），前端 Mac 宿主机直接启动
- 桥接网络 `172.30.90.0/24`，静态 IP `172.30.90.10`
- 端口映射 `8001:8000`（8000 被 online-code-runner 占用）
- 国产镜像源：`docker.m.daocloud.io/library/python:3.12-slim`

## 关键文件
- `backend/.env` — 真实密钥（Git 忽略）
- `backend/Dockerfile` — 后端镜像
- `docker-compose.yml` — 后端服务编排
- `scripts/check_mirrors.sh` — 国产镜像校验
- `scripts/export_images.sh` — 镜像导出

## 启动命令
```bash
# 后端
docker compose up -d backend

# 前端（在 Mac 宿主机）
cd frontend && npm run dev
```
