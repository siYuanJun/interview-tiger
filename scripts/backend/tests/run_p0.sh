#!/bin/bash
# 仅运行 P0 场景（健康检查 + 上传 + 验证）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 创建 venv
if [ ! -d "venv" ]; then
    echo ">>> 创建 Python venv ..."
    python3 -m venv venv
fi

# 安装依赖
echo ">>> 安装依赖 ..."
source venv/bin/activate
pip install -q -r requirements.txt

# 运行 P0 场景
echo ">>> 开始 P0 测试（跳过清理步骤）..."
echo ""
python -c "
import sys
from logger import setup_logger
from config import BASE_URL, REQUEST_TIMEOUT
from utils.http_client import ApiClient
import scene_s1_health, scene_s2_upload, scene_s3_verify

logger = setup_logger()
client = ApiClient(BASE_URL, logger, timeout=REQUEST_TIMEOUT)
scene_s1_health.run(client, logger)
scene_s2_upload.run(client, logger)
scene_s3_verify.run(client, logger)
"
