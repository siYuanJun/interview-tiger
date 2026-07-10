#!/usr/bin/env python3
"""
接口测试: POST /api/question/stream — SSE 流式验证
来源: question.py:119-176, main.py:88 prefix="/api"
生成时间: 2026-07-10
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8001"
SESSION_ID = f"stream-test-{int(time.time())}"


def test_stream(label, payload, expect):
    """来源: question.py:119-176"""
    url = f"{BASE_URL}/api/question/stream"
    print(f"\n{'='*60}")
    print(f"[TEST] {label}")
    print(f"[POST] {url}")
    print(f"[BODY] question='{payload['question'][:50]}' kb_provider={payload.get('kb_provider','')}")

    try:
        resp = requests.post(url, json=payload, stream=True, timeout=60)
        print(f"[STATUS] {resp.status_code}")

        if resp.status_code != 200:
            print(f"[RESULT] ❌ HTTP {resp.status_code}")
            return False

        events = []
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    event_type = data.get("type", "?")
                    events.append(event_type)

                    if event_type == "status":
                        print(f"  [SSE/status] {data.get('message', '')}")
                    elif event_type == "chunk":
                        print(f"  [SSE/chunk] {data.get('content', '')[:60]}...", end="\r")
                    elif event_type == "done":
                        print(f"\n  [SSE/done] knowledge_used={data.get('knowledge_used', False)}")
                    elif event_type == "error":
                        print(f"\n  [SSE/error] {data.get('message', '')}")
                except json.JSONDecodeError:
                    pass

        # 验证事件
        missing = [e for e in expect if e not in events]
        if missing:
            print(f"[RESULT] ⚠️ 缺少事件: {missing}")
            print(f"  收到事件: {events}")
        else:
            print(f"[RESULT] ✅ 通过 (收到事件: {events})")
            return True

        return len(missing) == 0

    except requests.exceptions.ConnectionError:
        print("[RESULT] ❌ 连接失败：后端未启动")
        return False
    except Exception as e:
        print(f"[RESULT] ❌ 异常: {e}")
        return False


def main():
    tests = [
        {
            "label": "SSE 流式 - 本地知识库",
            "payload": {
                "question": "什么是微服务？",
                "kb_provider": "local",
                "session_id": SESSION_ID,
            },
            "expect": ["status", "chunk", "done"],
        },
        {
            "label": "SSE 流式 - 火山引擎知识库",
            "payload": {
                "question": "Java中HashMap的工作原理",
            },
            "expect": ["status", "chunk", "done"],
        },
        {
            "label": "SSE 流式 - 多轮记忆跟进",
            "payload": {
                "question": "还有吗？",
                "kb_provider": "local",
                "session_id": SESSION_ID,
            },
            "expect": ["status", "chunk", "done"],
        },
    ]

    results = []
    for tc in tests:
        ok = test_stream(**tc)
        results.append((tc["label"], ok))
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"[SUMMARY]")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for label, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {label}")
    print(f"  通过: {passed}/{total}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
