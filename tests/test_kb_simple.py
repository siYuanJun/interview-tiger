#!/usr/bin/env python3
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

KB_API_KEY = os.getenv("KB_API_KEY", "")
KB_ID = os.getenv("KB_ID", "kb-ee95868bec0b4da8")
KB_HOST = "api-knowledgebase.mlp.cn-beijing.volces.com"
KB_PROJECT = os.getenv("KB_PROJECT", "default")

def test_kb_search_bearer():
    print("=" * 60)
    print("测试1: 知识库检索 (Bearer Token + resource_id)")
    print("=" * 60)
    
    print(f"📋 当前配置:")
    print(f"  KB_API_KEY: '{KB_API_KEY}'")
    print(f"  KB_ID (resource_id): '{KB_ID}'")
    print(f"  KB_PROJECT: '{KB_PROJECT}'")
    
    if not KB_API_KEY:
        print("\n❌ KB_API_KEY 为空")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KB_API_KEY}"
    }
    
    payload = {
        "resource_id": KB_ID,
        "project": KB_PROJECT,
        "query": "你叫什么",
        "limit": 2,
        "post_processing": {
            "rerank_switch": False,
            "retrieve_count": 25
        }
    }
    
    url = f"https://{KB_HOST}/api/knowledge/collection/search_knowledge"
    
    try:
        print(f"\n🚀 发送请求: POST {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"\n📄 响应体:")
        print(response.text)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                data = result.get('data', {})
                results = data.get('result_list', [])
                print(f"\n✅ 成功！检索到 {len(results)} 条结果:")
                for item in results:
                    score = item.get('score', 'N/A')
                    content = item.get('content', '')[:100]
                    print(f"   - 分数: {score}")
                    print(f"     内容: {content}...")
            else:
                print(f"\n❌ 业务错误: {result.get('message', 'Unknown')}")
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")

def test_kb_search_name():
    print("\n" + "=" * 60)
    print("测试2: 知识库检索 (Bearer Token + name)")
    print("=" * 60)
    
    if not KB_API_KEY:
        print("❌ KB_API_KEY 为空")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KB_API_KEY}"
    }
    
    payload = {
        "name": "siyuan_jianli",
        "project": KB_PROJECT,
        "query": "你叫什么",
        "limit": 2,
        "post_processing": {
            "rerank_switch": False,
            "retrieve_count": 25
        }
    }
    
    url = f"https://{KB_HOST}/api/knowledge/collection/search_knowledge"
    
    try:
        print(f"\n🚀 发送请求: POST {url}")
        print(f"📋 使用 name='siyuan_jianli'")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"\n📄 响应体:")
        print(response.text)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                data = result.get('data', {})
                results = data.get('result_list', [])
                print(f"\n✅ 成功！检索到 {len(results)} 条结果:")
                for item in results:
                    score = item.get('score', 'N/A')
                    content = item.get('content', '')[:100]
                    print(f"   - 分数: {score}")
                    print(f"     内容: {content}...")
            else:
                print(f"\n❌ 业务错误: {result.get('message', 'Unknown')}")
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")

if __name__ == "__main__":
    test_kb_search_bearer()
    test_kb_search_name()
