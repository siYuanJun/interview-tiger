#!/bin/bash

set -e

TEST_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$TEST_DIR"

echo "初始化测试环境..."

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -q -r requirements.txt

echo "运行P0场景测试..."
python main.py --p0

deactivate
