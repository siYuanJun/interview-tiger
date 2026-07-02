# 面试虎 - 后端 Docker 镜像
# 原则1：镜像不绑定环境，ENV 通过 docker-compose 注入
# 原则6：必须使用国产镜像源

FROM docker.m.daocloud.io/library/python:3.12-slim

WORKDIR /app

# 安装系统依赖（健康检查用 curl）
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖（使用清华源加速）
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制应用代码
COPY . .

# 数据持久化卷
VOLUME ["/app/data"]

EXPOSE 8000

# 通过 uvicorn 启动，--host 0.0.0.0 确保容器内可被外部访问
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
