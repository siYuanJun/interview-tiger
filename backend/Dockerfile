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

# 复制依赖清单和 wheel 缓存（总是存在）
COPY requirements.txt wheels/ /app/deps/

# 安装 Python 依赖（有快照则秒级恢复，无快照则 pip 在线安装）
# 注意：site-packages.tar.gz 是可选的，不存在会自动降级到网络安装
COPY . /tmp/build/
RUN if [ -f /tmp/build/site-packages.tar.gz ] && [ -s /tmp/build/site-packages.tar.gz ]; then \
        echo "[BUILD] ✅ site-packages 快照命中，秒级恢复..."; \
        tar xzf /tmp/build/site-packages.tar.gz -C /usr/local/lib/python3.12/; \
    else \
        echo "[BUILD] ⚠️  快照不存在，pip 在线安装（首次构建较慢）"; \
        pip install --no-cache-dir \
            --find-links=/tmp/build/wheels/ \
            -i https://pypi.tuna.tsinghua.edu.cn/simple \
            -r /tmp/build/requirements.txt; \
    fi && \
    cp /tmp/build/requirements.txt /app/requirements.txt && \
    rm -rf /tmp/build

# 复制应用代码
COPY . .

# 数据持久化卷
VOLUME ["/app/data"]

EXPOSE 8000

# 通过 uvicorn 启动，--host 0.0.0.0 确保容器内可被外部访问
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
