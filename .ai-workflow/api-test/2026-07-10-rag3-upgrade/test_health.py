#!/usr/bin/env python3
"""
接口测试: GET /api/health
来源: health.py:7, main.py:83 prefix="/api"
生成时间: 2026-07-10
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8001"


def test_health():
    """测试健康检查 + RAG3 模块初始化"""
    url = f"{BASE_URL}/api/health"

    print(f"[TEST] GET {url}")
    try:
        resp = requests.get(url, timeout=5)
        print(f"[STATUS] {resp.status_code}")
        print(f"[RESPONSE] {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")

        if resp.status_code == 200:
            print("[RESULT] ✅ 健康检查通过")
            return True
        else:
            print(f"[RESULT] ❌ 失败 (HTTP {resp.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("[RESULT] ❌ 连接失败：后端未启动或端口错误")
        return False
    except Exception as e:
        print(f"[RESULT] ❌ 异常: {e}")
        return False


if __name__ == "__main__":
    success = test_health()
    sys.exit(0 if success else 1)
