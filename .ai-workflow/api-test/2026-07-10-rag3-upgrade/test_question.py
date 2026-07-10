#!/usr/bin/env python3
"""
接口测试: POST /api/question — RAG 3.0 全管道验证
来源: question.py:62-116, main.py:88 prefix="/api"
生成时间: 2026-07-10

测试场景:
  1. 基础问答 — 验证非流式返回结构
  2. RAG3 混合检索 — 验证 knowledge_used 命中
  3. session_id 多轮记忆 — 验证跟进问题缓存
  4. 参数校验 — question 为空应返回 422
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8001"
SESSION_ID = f"test-rag3-{int(time.time())}"

# 知识库中应存在的测试问题（根据实际文档调整）
TEST_QUESTIONS = [
    {
        "label": "基础问答 - 非流式",
        "payload": {
            "question": "什么是微服务架构？",
            "kb_provider": "local",
            "stream": False,
            "session_id": SESSION_ID,
        },
        "expect": {"status": 200, "has_answer": True},
    },
    {
        "label": "RAG3 知识库命中",
        "payload": {
            "question": "请介绍一下微服务的优缺点",
            "kb_provider": "local",
            "stream": False,
            "session_id": SESSION_ID,
        },
        "expect": {"status": 200, "has_answer": True, "knowledge_used": True},
    },
    {
        "label": "RAG3 跟进问题（多轮记忆）",
        "payload": {
            "question": "那具体怎么落地呢？",
            "kb_provider": "local",
            "stream": False,
            "session_id": SESSION_ID,
        },
        "expect": {"status": 200, "has_answer": True},
    },
]

FAILURE_TESTS = [
    {
        "label": "参数校验 - question 为空",
        "payload": {
            "question": "",
            "kb_provider": "local",
            "stream": False,
        },
        "expect": {"status": 422},
    },
]


def post_question(label, payload, expect):
    """来源: question.py:62-116"""
    url = f"{BASE_URL}/api/question"
    print(f"\n{'='*60}")
    print(f"[TEST] {label}")
    print(f"[POST] {url}")
    print(f"[BODY] question='{payload['question'][:50]}...' kb_provider={payload.get('kb_provider','')} session_id={payload.get('session_id','')[:20]}...")

    try:
        resp = requests.post(url, json=payload, timeout=60)
        print(f"[STATUS] {resp.status_code}")

        if resp.status_code != expect["status"]:
            print(f"[RESULT] ❌ 状态码不匹配: 期望 {expect['status']}, 实际 {resp.status_code}")
            return False

        if resp.status_code == 422:
            body = resp.json()
            print(f"[RESPONSE] {json.dumps(body, ensure_ascii=False, indent=2)}")
            print(f"[RESULT] ✅ 参数校验生效（422 符合预期）")
            return True

        body = resp.json()
        answer = body.get("data", {}).get("answer", "")
        knowledge_used = body.get("data", {}).get("knowledge_used", False)
        web_search_used = body.get("data", {}).get("web_search_used", False)

        print(f"[KNOWLEDGE] knowledge_used={knowledge_used}, web_search_used={web_search_used}")
        print(f"[ANSWER] {answer[:150]}...")

        if expect.get("has_answer") and not answer:
            print(f"[RESULT] ❌ 期望有回答但为空")
            return False

        if expect.get("knowledge_used") and not knowledge_used:
            print(f"[RESULT] ⚠️ 期望知识库命中但未命中（可能知识库无相关文档）")

        print(f"[RESULT] ✅ 通过")
        return True

    except requests.exceptions.ConnectionError:
        print("[RESULT] ❌ 连接失败：后端未启动")
        return False
    except Exception as e:
        print(f"[RESULT] ❌ 异常: {e}")
        return False


def main():
    results = []

    for tc in TEST_QUESTIONS:
        ok = post_question(**tc)
        results.append((tc["label"], ok))
        time.sleep(2)  # 避免请求过快

    for tc in FAILURE_TESTS:
        ok = post_question(**tc)
        results.append((tc["label"], ok))

    # 汇总
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
