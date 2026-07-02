# 后端配置文件
import os
from dotenv import load_dotenv

load_dotenv()

# 火山引擎方舟大模型
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_MODEL = os.getenv("ARK_MODEL", "deepseek-v4-flash-260425")
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

# 火山引擎知识库
KB_API_KEY = os.getenv("KB_API_KEY", "")
KB_ID = os.getenv("KB_ID", "siyuan_jianli")
KB_PROJECT = os.getenv("KB_PROJECT", "default")
KB_BASE_URL = os.getenv("KB_BASE_URL", "https://api-knowledgebase.mlp.cn-beijing.volces.com")

# 服务配置
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
