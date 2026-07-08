#!/usr/bin/env python3
"""
接口测试: POST /api/question/stream (SSE流式接口)
来源: backend/app/routes/question.py:113
生成时间: 2026-07-08
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:40003"

def test_question_stream():
    """测试面试问题流式接口"""
    url = f"{BASE_URL}/api/question/stream"
    
    payload = {
        "question": "他也别想",
        "ark_api_key": "",
        "model_id": "deepseek-v4-flash-260425",
        "kb_id": "kb-ee95868bec0b4da8",
        "kb_api_key": "",
        "kb_provider": "volcengine",
        "stream": True
    }
    
    print(f"[TEST] POST {url}")
    print(f"[BODY] {json.dumps(payload, ensure_ascii=False)}")
    print("-" * 60)
    
    results = {
        "status_code": None,
        "headers": {},
        "events": [],
        "full_content": "",
        "error": None,
        "success": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=60, stream=True)
        results["status_code"] = resp.status_code
        results["headers"] = dict(resp.headers)
        
        print(f"[STATUS] {resp.status_code}")
        print(f"[CONTENT-TYPE] {resp.headers.get('Content-Type', 'N/A')}")
        
        if resp.status_code != 200:
            print(f"[RESPONSE] {resp.text[:500]}")
            print(f"[RESULT] ❌ 失败 (HTTP {resp.status_code})")
            results["error"] = f"HTTP {resp.status_code}"
            with open("test_result.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            sys.exit(1)
        
        print("[STREAM] 开始接收 SSE 数据...")
        print("-" * 60)
        
        start_time = time.time()
        event_count = 0
        full_content = ""
        
        for line in resp.iter_lines(chunk_size=1024):
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_part = line_str[6:]
                    event_count += 1
                    
                    if data_part == "[DONE]":
                        print(f"[EVENT {event_count}] type: done")
                        results["events"].append({"type": "done", "content": "[DONE]"})
                        break
                    
                    try:
                        data = json.loads(data_part)
                        event_type = data.get("type", "unknown")
                        content = data.get("content", "")
                        message = data.get("message", "")
                        
                        if event_type == "status":
                            print(f"[EVENT {event_count}] type: status, message: {message}")
                            results["events"].append({"type": "status", "message": message})
                        elif event_type == "chunk":
                            print(f"[EVENT {event_count}] type: chunk, content: {content}")
                            full_content += content
                            results["events"].append({"type": "chunk", "content": content})
                        elif event_type == "error":
                            print(f"[EVENT {event_count}] type: error, message: {message}")
                            results["events"].append({"type": "error", "message": message})
                            results["error"] = message
                        else:
                            print(f"[EVENT {event_count}] type: {event_type}, data: {data_part[:100]}")
                            results["events"].append({"type": event_type, "raw": data_part})
                    except json.JSONDecodeError:
                        print(f"[EVENT {event_count}] raw: {line_str[:100]}")
                        results["events"].append({"type": "raw", "content": line_str})
        
        elapsed_time = time.time() - start_time
        results["full_content"] = full_content
        results["success"] = True
        
        print("-" * 60)
        print(f"[SUMMARY] 共接收 {event_count} 个事件，耗时 {elapsed_time:.2f}s")
        print(f"[FULL_CONTENT] {full_content}")
        print("[RESULT] ✅ 通过")
        
        with open("test_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
    except requests.exceptions.ConnectionError:
        print("[RESULT] ❌ 连接失败：服务未启动或端口错误")
        results["error"] = "ConnectionError: 服务未启动或端口错误"
        with open("test_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("[RESULT] ❌ 请求超时")
        results["error"] = "Timeout: 请求超时"
        with open("test_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        sys.exit(1)
    except Exception as e:
        print(f"[RESULT] ❌ 异常: {e}")
        results["error"] = str(e)
        with open("test_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        sys.exit(1)

if __name__ == "__main__":
    test_question_stream()