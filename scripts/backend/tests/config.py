"""测试配置"""
import os
from pathlib import Path

# --- 服务地址 ---
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8001")

# --- 测试用文件 ---
# 真实的面试知识库文件
TEST_FILE_PATH = os.getenv(
    "TEST_FILE_PATH",
    str(Path.home() / "Documents/个人信息/简历/简历内容/docs/知识库/面试知识库-整理版/01-自我介绍与核心必答题.md")
)

# --- 请求超时（秒） ---
REQUEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "120"))

# --- 上传参数 ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- 检索参数 ---
SEARCH_QUERY = "自我介绍"
SEARCH_TOP_K = 5
