# 后端配置文件
import os
from dotenv import load_dotenv

load_dotenv()

# 火山引擎方舟大模型
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_MODEL = os.getenv("ARK_MODEL", "deepseek-v4-flash-260425")
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

# 知识库配置
KB_PROVIDER = os.getenv("KB_PROVIDER", "volcengine")
KB_API_KEY = os.getenv("KB_API_KEY", "")
KB_ID = os.getenv("KB_ID", "kb-ee95868bec0b4da8")
KB_PROJECT = os.getenv("KB_PROJECT", "default")
KB_BASE_URL = os.getenv("KB_BASE_URL", "https://api-knowledgebase.mlp.cn-beijing.volces.com")
KB_ACCOUNT_ID = os.getenv("KB_ACCOUNT_ID", "")  # SignerV4 签名必需

# 本地知识库配置
LOCAL_KB_DATA_DIR = os.getenv("LOCAL_KB_DATA_DIR", "./data/chroma")
LOCAL_KB_EMBEDDING_MODEL = os.getenv("LOCAL_KB_EMBEDDING_MODEL", "bge-large-zh-v1.5")
LOCAL_KB_CHUNK_SIZE = int(os.getenv("LOCAL_KB_CHUNK_SIZE", "500"))
LOCAL_KB_CHUNK_OVERLAP = int(os.getenv("LOCAL_KB_CHUNK_OVERLAP", "50"))

# 联网搜索配置（知识库无结果时的降级方案）
# WEB_SEARCH_BOT_ID: Bot应用ID，用于联网搜索（在方舟控制台创建Bot并开通联网插件后获取）
WEB_SEARCH_BOT_ID = os.getenv("WEB_SEARCH_BOT_ID", "")

# 火山引擎语音识别（ASR）— 豆包同款引擎
ASR_APP_ID = os.getenv("ASR_APP_ID", "")
ASR_TOKEN = os.getenv("ASR_TOKEN", "")
ASR_CLUSTER = os.getenv("ASR_CLUSTER", "volcengine_streaming_common")
ASR_WS_URL = os.getenv("ASR_WS_URL", "wss://openspeech.bytedance.com/api/v2/asr")

# 服务配置
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"

# CORS 配置 - 支持多个前端域名
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:your_password@localhost:5432/interview_tiger")
