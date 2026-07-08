#!/bin/bash
# 一键运行所有测试（自动创建 venv）
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

# 运行测试
echo ">>> 开始测试 ..."
echo ""
python main.py
