#!/usr/bin/env python3
"""
签名调试脚本 - 完全按照官方示例代码测试
"""
import json
import sys
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

# 从.env读取配置
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from config import KB_API_KEY, KB_ID

if ':' not in KB_API_KEY:
    print("错误：KB_API_KEY格式不正确，期望 AK:SK 格式")
    sys.exit(1)

ak, sk = KB_API_KEY.split(':', 1)
print(f"AK: {ak}")
print(f"SK长度: {len(sk)}")

# 官方示例的签名函数
def prepare_request(method, path, ak, sk, params=None, data=None, doseq=0):
    if params:
        for key in params:
            if (
                type(params[key]) == int
                or type(params[key]) == float
                or type(params[key]) == bool
            ):
                params[key] = str(params[key])
            elif type(params[key]) == list:
                if not doseq:
                    params[key] = ",".join(params[key])
    
    r = Request()
    r.set_shema("https")
    r.set_method(method)
    r.set_connection_timeout(10)
    r.set_socket_timeout(10)
    
    mheaders = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Host": "api-knowledgebase.mlp.cn-beijing.volces.com",
    }
    r.set_headers(mheaders)
    
    if params:
        r.set_query(params)
    
    r.set_host("api-knowledgebase.mlp.cn-beijing.volces.com")
    r.set_path(path)
    
    if data is not None:
        r.set_body(json.dumps(data))
    
    credentials = Credentials(ak, sk, "air", "cn-north-1")
    SignerV4.sign(r, credentials)
    
    return r

# 测试1: 获取知识库列表
print("\n=== 测试1: 获取知识库列表 ===")
path = "/api/knowledge/collection/list"
payload = {
    "project": "default",
    "page_size": 20,
    "page_num": 1
}

req = prepare_request("POST", path, ak, sk, data=payload)
print(f"请求方法: {req.method}")
print(f"请求路径: {req.path}")
print(f"请求体: {req.body}")
print(f"请求头: {dict(req.headers)}")

try:
    url = f"https://{req.host}{req.path}"
    print(f"完整URL: {url}")
    
    response = requests.post(
        url,
        headers=dict(req.headers),
        data=req.body,
        timeout=30
    )
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应体: {response.text[:1000]}")
except Exception as e:
    print(f"请求失败: {e}")

# 测试2: 搜索知识库
print("\n=== 测试2: 搜索知识库 ===")
path = "/api/knowledge/collection/search_knowledge"
payload = {
    "resource_id": KB_ID,
    "project": "default",
    "query": "你叫什么？",
    "limit": 3,
    "post_processing": {
        "rerank_switch": True,
        "retrieve_count": 25
    }
}

req = prepare_request("POST", path, ak, sk, data=payload)
print(f"请求方法: {req.method}")
print(f"请求路径: {req.path}")
print(f"请求体: {req.body}")
print(f"请求头: {dict(req.headers)}")

try:
    url = f"https://{req.host}{req.path}"
    print(f"完整URL: {url}")
    
    response = requests.post(
        url,
        headers=dict(req.headers),
        data=req.body,
        timeout=30
    )
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应体: {response.text[:1000]}")
except Exception as e:
    print(f"请求失败: {e}")
