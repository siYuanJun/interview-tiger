#!/usr/bin/env python3
"""
测试火山引擎知识库检索接口（多种认证方式）
根据《字节跳动接口调用指南.md》文档和官方文档实现
依赖: pip install requests volcengine==1.0.0
"""

import os
import json
import requests
from dotenv import load_dotenv
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

KB_API_KEY = os.getenv("KB_API_KEY", "")
KB_ID = os.getenv("KB_ID", "siyuan_jianli")
KB_PROJECT = os.getenv("KB_PROJECT", "default")
KB_HOST = "api-knowledgebase.mlp.cn-beijing.volces.com"
KB_ACCOUNT_ID = os.getenv("KB_ACCOUNT_ID", "")

TEST_QUERY = "你叫什么"


def sign_request(method, path, ak, sk, data=None, extra_headers=None, service="air", region="cn-north-1"):
    r = Request()
    r.set_shema("https")
    r.set_method(method)
    r.set_connection_timeout(10)
    r.set_socket_timeout(10)
    
    mheaders = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Host": KB_HOST
    }
    
    if extra_headers:
        mheaders.update(extra_headers)
    
    r.set_headers(mheaders)
    r.set_host(KB_HOST)
    r.set_path(path)
    
    if data is not None:
        r.set_body(json.dumps(data))
    
    credentials = Credentials(ak, sk, service, region)
    SignerV4.sign(r, credentials)
    
    return r.headers, r.body


def check_config():
    issues = []
    
    if not KB_API_KEY:
        issues.append("❌ KB_API_KEY 为空")
    elif ':' not in KB_API_KEY:
        issues.append("⚠️ KB_API_KEY 不是 AK:SK 格式（缺少冒号分隔）")
    elif not KB_API_KEY.startswith('AKLT'):
        issues.append("⚠️ KB_API_KEY 的 AK 部分不是以 AKLT 开头")
    
    if not KB_ID:
        issues.append("❌ KB_ID 为空")
    elif not KB_ID.startswith('kb-'):
        issues.append("⚠️ KB_ID 不是标准格式（应为 kb-xxx）")
    
    if not KB_ACCOUNT_ID:
        issues.append("❌ KB_ACCOUNT_ID 为空 - 这是签名认证必需的参数")
    
    if issues:
        print("\n❌ 配置检查失败:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print("\n✅ 配置检查通过")
    return True


def test_signerv4():
    if not KB_API_KEY or ':' not in KB_API_KEY:
        print("❌ KB_API_KEY 无效，跳过 SignerV4 测试")
        return False
    
    ak, sk = KB_API_KEY.split(':', 1)
    path = '/api/knowledge/collection/search_knowledge'
    url = f"https://{KB_HOST}{path}"
    
    payload = {
        "resource_id": KB_ID,
        "project": KB_PROJECT,
        "query": TEST_QUERY,
        "limit": 3,
        "post_processing": {
            "rerank_switch": True,
            "retrieve_count": 25
        }
    }
    
    headers_to_try = []
    if KB_ACCOUNT_ID:
        headers_to_try.append({"name": "V-Account-Id", "headers": {"V-Account-Id": KB_ACCOUNT_ID}})
        headers_to_try.append({"name": "Tenant-Id", "headers": {"Tenant-Id": KB_ACCOUNT_ID}})
        headers_to_try.append({"name": "x-tenant", "headers": {"x-tenant": KB_ACCOUNT_ID}})
    else:
        headers_to_try.append({"name": "无额外头", "headers": {}})
    
    for ht in headers_to_try:
        print(f"\n📤 测试 {ht['name']}...")
        try:
            headers, body = sign_request('POST', path, ak, sk, payload, ht['headers'])
            response = requests.post(url, headers=headers, data=body, timeout=30)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    results = result.get('data', {}).get('result_list', [])
                    print(f"\n✅ 成功！检索到 {len(results)} 条结果")
                    for i, item in enumerate(results, 1):
                        score = item.get('score', 'N/A')
                        rerank_score = item.get('rerank_score', 'N/A')
                        content = item.get('content', '')[:100]
                        print(f"\n   [{i}] score: {score}, rerank_score: {rerank_score}")
                        print(f"       content: {content}...")
                    return True
            
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    return False


def test_enterprise_knowledge_engine():
    print("\n" + "=" * 50)
    print("测试: 企业知识引擎 API")
    print("=" * 50)
    
    if not KB_ACCOUNT_ID:
        print("⚠️ KB_ACCOUNT_ID 为空，跳过企业知识引擎测试")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KB_API_KEY}",
        "x-tenant": KB_ACCOUNT_ID,
        "x-org": KB_ACCOUNT_ID
    }
    
    payload = {
        "kb_id": KB_ID,
        "query": TEST_QUERY,
        "top_k": 3
    }
    
    urls = [
        ("profile_platform", f"https://{KB_HOST}/profile_platform/api/v2/rag/search"),
        ("api/v2", f"https://{KB_HOST}/api/v2/rag/search"),
    ]
    
    for name, url in urls:
        print(f"\n🚀 {name}: POST {url}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ 成功！")
                print(f"   响应: {json.dumps(result, ensure_ascii=False)[:300]}")
                return True
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    return False


def main():
    print("=" * 70)
    print("火山引擎知识库测试工具")
    print("=" * 70)
    
    print(f"\n📋 当前配置:")
    print(f"  KB_API_KEY: '{KB_API_KEY}'")
    print(f"  KB_ID: '{KB_ID}'")
    print(f"  KB_PROJECT: '{KB_PROJECT}'")
    print(f"  KB_HOST: '{KB_HOST}'")
    print(f"  KB_ACCOUNT_ID: '{KB_ACCOUNT_ID}'")
    print(f"  查询词: '{TEST_QUERY}'")
    
    check_config()
    
    print("\n" + "=" * 50)
    print("测试: SignerV4 签名方式")
    print("=" * 50)
    
    success = test_signerv4()
    
    if not success:
        success = test_enterprise_knowledge_engine()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 测试成功！")
    else:
        print("❌ 测试失败！")
    print("=" * 70)
    
    if not success:
        print("\n" + "=" * 70)
        print("🔍 故障排查指南")
        print("=" * 70)
        print("\n1. 检查 AK/SK 是否正确")
        print("   - 登录火山引擎控制台 → 右上角头像 → API 访问密钥")
        print("   - 确认 AK 以 AKLT 开头")
        print("   - 确认 SK 是完整的密钥字符串")
        
        print("\n2. 检查 KB_ACCOUNT_ID（最可能的问题）")
        print("   - 错误信息明确提示需要 tenant id")
        print("   - 在后端/.env 文件中配置 KB_ACCOUNT_ID")
        print("   - 获取方式：登录火山引擎控制台 → 查看URL中的数字部分")
        
        print("\n3. 确认知识库服务已开通")
        print("   - 前往 https://console.volcengine.com/ark/")
        print("   - 确认知识库服务已开通")
        
        print("\n4. 确认 KB_ID 格式正确")
        print("   - 格式应为: kb-xxx")
        print("   - 当前 KB_ID: " + KB_ID)
        
        print("\n5. 如果使用企业知识引擎")
        print("   - 需要使用 Bearer Token 格式的 API Key")
        print("   - 需要配置 x-tenant 和 x-org 请求头")
        print("   - API Key 需要在企业知识引擎控制台获取")


if __name__ == "__main__":
    main()  
