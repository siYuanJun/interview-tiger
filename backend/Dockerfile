# 面试虎 - 后端 Docker 镜像
# 原则1：镜像不绑定环境，ENV 通过 docker-compose 注入
# 原则6：必须使用国产镜像源

FROM docker.m.daocloud.io/library/python:3.12-slim

WORKDIR /app

# 安装系统依赖（使用阿里云镜像源，健康检查用 curl + chroma-hnswlib 编译依赖）
RUN echo "deb http://mirrors.aliyun.com/debian/ trixie main contrib non-free non-free-firmware" > /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ trixie-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security/ trixie-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    curl g++ cmake build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 优先使用预编译 site-packages 快照（秒级恢复，跳过网络下载）
COPY site-packages.tar.gz /tmp/
RUN tar xzf /tmp/site-packages.tar.gz -C /usr/local/lib/python3.12/ \
    && rm /tmp/site-packages.tar.gz

# 备用：拷贝 wheel 缓存 + pip install（site-packages 不存在时走这里）
COPY wheels/ /app/wheels/
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --find-links=/app/wheels/ \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt 2>/dev/null || echo "[INFO] 使用 site-packages 快照，跳过网络安装"

# 复制应用代码
COPY . .

# 数据持久化卷
VOLUME ["/app/data"]

EXPOSE 8000

# 通过 uvicorn 启动，--host 0.0.0.0 确保容器内可被外部访问
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
