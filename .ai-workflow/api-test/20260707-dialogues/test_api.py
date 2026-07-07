#!/usr/bin/env python3
"""
接口测试: GET /api/dialogues
来源: transcript.py:87
生成时间: 2026-07-07
"""
import requests
import json
import sys

BASE_URL = "http://localhost:40003"

def test_get_dialogues():
    url = f"{BASE_URL}/api/dialogues"
    
    test_cases = [
        {"name": "按session_id查询", "params": {"session_id": "session_1783434223843_ynl6rb59b"}},
        {"name": "查询所有对话", "params": {}}
    ]
    
    for tc in test_cases:
        print(f"\n[TEST] {tc['name']}")
        print(f"[URL] GET {url}")
        if tc["params"]:
            print(f"[PARAMS] {json.dumps(tc['params'], ensure_ascii=False)}")
        
        try:
            resp = requests.get(url, params=tc["params"], timeout=10)
            print(f"[STATUS] {resp.status_code}")
            print(f"[RESPONSE] {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    print("[RESULT] ✅ 通过")
                else:
                    print(f"[RESULT] ⚠️ 业务错误: {data.get('message')}")
            else:
                print(f"[RESULT] ❌ 失败 (HTTP {resp.status_code})")
        except requests.exceptions.ConnectionError:
            print("[RESULT] ❌ 连接失败：服务未启动或端口错误")
            sys.exit(1)
        except Exception as e:
            print(f"[RESULT] ❌ 异常: {e}")

if __name__ == "__main__":
    test_get_dialogues()
