#!/usr/bin/env python3
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"
SUCCESS_CODE = 0

passed = 0
failed = 0

def log_pass(msg):
    global passed
    passed += 1
    print(f"✅ PASS: {msg}")

def log_fail(msg, error=None):
    global failed
    failed += 1
    print(f"❌ FAIL: {msg}")
    if error:
        print(f"   Error: {error}")

def test_health():
    print("\n--- 测试健康检查接口 /health ---")
    try:
        res = requests.get(f"{BASE_URL}/health")
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == SUCCESS_CODE:
                log_pass("健康检查接口正常")
            else:
                log_fail(f"健康检查返回码错误: {data.get('code')}")
        else:
            log_fail(f"健康检查状态码错误: {res.status_code}")
    except Exception as e:
        log_fail("健康检查请求失败", str(e))

def test_config_get():
    print("\n--- 测试配置获取接口 /config ---")
    try:
        res = requests.get(f"{BASE_URL}/config")
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == SUCCESS_CODE:
                log_pass("配置获取接口正常")
            else:
                log_fail(f"配置获取返回码错误: {data.get('code')}")
        else:
            log_fail(f"配置获取状态码错误: {res.status_code}")
    except Exception as e:
        log_fail("配置获取请求失败", str(e))

def test_config_post():
    print("\n--- 测试配置保存接口 POST /config ---")
    try:
        config_data = {
            "ark_api_key": "test_key_123",
            "kb_id": "test_kb_123",
            "model_id": "test_model_123"
        }
        res = requests.post(f"{BASE_URL}/config", json=config_data)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == SUCCESS_CODE:
                log_pass("配置保存接口正常")
            else:
                log_fail(f"配置保存返回码错误: {data.get('code')}")
        else:
            log_fail(f"配置保存状态码错误: {res.status_code}")
    except Exception as e:
        log_fail("配置保存请求失败", str(e))

def test_transcript():
    print("\n--- 测试识别文本提交接口 POST /transcript ---")
    try:
        requests.delete(f"{BASE_URL}/dialogues")
        
        test_cases = [
            {"text": "你好", "should_be_valid": False, "reason": "非疑问句"},
            {"text": "什么是React?", "should_be_valid": True},
            {"text": "请介绍一下你的工作经历", "should_be_valid": True},
            {"text": "能说一下你参与的项目吗", "should_be_valid": True},
        ]
        
        for case in test_cases:
            res = requests.post(f"{BASE_URL}/transcript", json={"text": case["text"]})
            if res.status_code == 200:
                data = res.json()
                is_valid = data.get("data", {}).get("is_valid", False)
                if is_valid == case["should_be_valid"]:
                    log_pass(f"文本识别: '{case['text']}' -> {'有效' if is_valid else '无效'}")
                else:
                    log_fail(f"文本识别判断错误: '{case['text']}' 期望{'有效' if case['should_be_valid'] else '无效'}，实际{'有效' if is_valid else '无效'}")
            else:
                log_fail(f"文本识别状态码错误: {res.status_code}")
    except Exception as e:
        log_fail("文本识别请求失败", str(e))

def test_dialogues():
    print("\n--- 测试对话列表接口 GET /dialogues ---")
    try:
        res = requests.get(f"{BASE_URL}/dialogues")
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == SUCCESS_CODE:
                dialogues = data.get("data", {}).get("dialogues", [])
                log_pass(f"对话列表接口正常，当前对话数: {len(dialogues)}")
            else:
                log_fail(f"对话列表返回码错误: {data.get('code')}")
        else:
            log_fail(f"对话列表状态码错误: {res.status_code}")
    except Exception as e:
        log_fail("对话列表请求失败", str(e))

def test_dialogues_clear():
    print("\n--- 测试清空对话接口 DELETE /dialogues ---")
    try:
        res = requests.delete(f"{BASE_URL}/dialogues")
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == SUCCESS_CODE:
                log_pass("清空对话接口正常")
            else:
                log_fail(f"清空对话返回码错误: {data.get('code')}")
        else:
            log_fail(f"清空对话状态码错误: {res.status_code}")
    except Exception as e:
        log_fail("清空对话请求失败", str(e))

def test_question_stream():
    print("\n--- 测试问题处理接口（流式）POST /question/stream ---")
    try:
        test_data = {
            "question": "你好",
            "ark_api_key": "",
            "model_id": "test"
        }
        res = requests.post(f"{BASE_URL}/question/stream", json=test_data, stream=True, timeout=30)
        if res.status_code == 400:
            log_pass("流式接口参数校验正常（无API Key返回400）")
        elif res.status_code == 200:
            content = ""
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    content += chunk.decode('utf-8')
            if "data:" in content:
                log_pass("流式接口返回格式正确")
            else:
                log_fail("流式接口返回格式错误")
        else:
            log_fail(f"流式接口状态码错误: {res.status_code}")
    except requests.exceptions.HTTPError as e:
        if "400" in str(e):
            log_pass("流式接口参数校验正常")
        else:
            log_fail("流式接口请求失败", str(e))
    except Exception as e:
        log_fail("流式接口请求失败", str(e))

def test_question_non_stream():
    print("\n--- 测试问题处理接口（非流式）POST /question ---")
    try:
        test_data = {
            "question": "你好",
            "ark_api_key": "",
            "model_id": "test",
            "stream": False
        }
        res = requests.post(f"{BASE_URL}/question", json=test_data, timeout=30)
        if res.status_code == 400:
            log_pass("非流式接口参数校验正常（无API Key返回400）")
        elif res.status_code == 200:
            data = res.json()
            if data.get("code") == SUCCESS_CODE:
                log_pass("非流式接口正常")
            else:
                log_fail(f"非流式接口返回码错误: {data.get('code')}")
        elif res.status_code == 500:
            log_pass("非流式接口返回500（预期：无有效API Key）")
        else:
            log_fail(f"非流式接口状态码错误: {res.status_code}")
    except requests.exceptions.HTTPError as e:
        if "400" in str(e):
            log_pass("非流式接口参数校验正常")
        elif "500" in str(e):
            log_pass("非流式接口返回500（预期：无有效API Key）")
        else:
            log_fail("非流式接口请求失败", str(e))
    except Exception as e:
        log_fail("非流式接口请求失败", str(e))

def run_all_tests():
    print("=" * 60)
    print("🎯 面试虎 API 接口测试")
    print("=" * 60)
    
    test_health()
    test_config_get()
    test_config_post()
    test_transcript()
    test_dialogues()
    test_dialogues_clear()
    test_question_stream()
    test_question_non_stream()
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed} 个通过, {failed} 个失败")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    run_all_tests()