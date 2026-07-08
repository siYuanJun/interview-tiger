# HuggingFace 模型离线部署方案

> 背景：Docker 容器内无法直连 huggingface.co，需要用国内镜像预下载后挂载。  
> 日期：2026-07-09

---

## 一、下载模型（宿主机执行）

```bash
# 1. 安装工具
pip install huggingface_hub

# 2. 走国内镜像下载（以 bge-small-zh-v1.5 为例，约 100MB）
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download BAAI/bge-small-zh-v1.5
```

下载后缓存位置：`~/.cache/huggingface/hub/models--BAAI--bge-small-zh-v1.5/`

---

## 二、挂载进容器

`docker-compose.yml` 的 backend 服务 volumes 加一行：

```yaml
backend:
  volumes:
    - ./backend:/app
    - ~/.cache/huggingface:/root/.cache/huggingface   # ← 挂载模型缓存
```

---

## 三、配置模型名

`backend/.env`：

```bash
LOCAL_KB_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

---

## 四、重启验证

```bash
docker-compose down backend && docker-compose up -d backend

# 等 healthy 后验证
curl -s http://localhost:8001/api/local_kb/stats | python3 -m json.tool
```

不报 500 即成功。sentence-transformers 加载时会先查本地缓存，命中就不走网络。

---

## 五、可选模型参考

| 模型 | 大小 | 场景 |
|------|------|------|
| `BAAI/bge-small-zh-v1.5` | ~100MB | 默认推荐，小规模够用 |
| `BAAI/bge-base-zh-v1.5` | ~400MB | 精度要求较高 |
| `BAAI/bge-large-zh-v1.5` | ~1.3GB | 极致精度，一般不需要 |

**选模型原则**：知识库不超过千级文档 → small 足够，不要上来就用 large。
