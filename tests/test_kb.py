#!/usr/bin/env python3
"""
知识库测试脚本 - 验证知识库是否正确生效

使用方法:
    python test_kb.py "你叫什么？"
    python test_kb.py "你会什么？"

期望结果:
    回答中应包含 "xxx" 才表示知识库生效
"""

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config import ARK_API_KEY, ARK_MODEL, KB_ID, KB_API_KEY


def test_knowledge_base(query: str):
    """测试知识库检索"""
    print(f"\n{'='*60}")
    print(f"测试查询: {query}")
    print(f"{'='*60}")

    # 测试0: 获取知识库列表，验证API Key和KB_ID格式
    print("\n【测试0: 获取知识库列表】")
    try:
        from app.services.knowledge import list_knowledge_bases
        
        if KB_API_KEY:
            kb_list = list_knowledge_bases(KB_API_KEY)
            print(f"API Key配置: {'有' if KB_API_KEY else '无'}")
            print(f"当前配置的KB_ID: {KB_ID}")
            print(f"\n知识库列表响应:")
            print(f"  {json.dumps(kb_list, indent=2, ensure_ascii=False)[:1000]}...")
            
            if 'data' in kb_list:
                collections = kb_list['data'].get('collection_list', kb_list['data'].get('collections', []))
                print(f"\n  可用知识库列表 ({len(collections)}个):")
                for kb in collections:
                    kb_id = kb.get('resource_id', kb.get('id', ''))
                    kb_name = kb.get('collection_name', kb.get('name', ''))
                    kb_status = kb.get('status', '')
                    is_current = "★" if kb_id == KB_ID else " "
                    print(f"  {is_current} ID: {kb_id}, 名称: {kb_name}, 状态: {kb_status}")
            else:
                print(f"  ⚠️  未获取到知识库列表，请检查API Key或网络")
        else:
            print(f"  ⚠️  KB_API_KEY未配置")
    except Exception as e:
        print(f"  ✗ 获取知识库列表失败: {e}")

    knowledge = ""
    
    # 测试1: 直接检索知识库
    print("\n【测试1: 知识库检索】")
    try:
        from app.services.knowledge import search_knowledge, get_relevant_knowledge
        
        if KB_ID and KB_API_KEY:
            raw_result = search_knowledge(query, KB_ID, KB_API_KEY)
            print(f"知识库ID: {KB_ID}")
            print(f"原始响应: {json.dumps(raw_result, indent=2, ensure_ascii=False)[:500]}...")
            
            knowledge = get_relevant_knowledge(query, KB_ID, KB_API_KEY)
            print(f"\n过滤后知识内容:")
            if knowledge:
                print(f"  ✓ 命中 {len(knowledge)} 字")
                print(f"  内容: {knowledge[:300]}...")
            else:
                print(f"  ✗ 未命中知识库")
        else:
            print(f"  ⚠️  知识库未配置 (KB_ID={KB_ID}, KB_API_KEY={KB_API_KEY})")
    except Exception as e:
        print(f"  ✗ 知识库检索失败: {e}")

    # 测试2: 调用大模型（有知识库）
    print("\n【测试2: 大模型调用（含知识库）】")
    try:
        from app.services.prompt import build_messages
        from app.services.llm import call_llm
        
        if ARK_API_KEY:
            knowledge_context = knowledge if 'knowledge' in locals() else ""
            if not knowledge_context and KB_ID and KB_API_KEY:
                knowledge_context = get_relevant_knowledge(query, KB_ID, KB_API_KEY)
            
            messages = build_messages(query, knowledge_context)
            print(f"知识库上下文: {'有' if knowledge_context else '无'}")
            print(f"Prompt长度: {len(messages[0]['content'])} 字")
            
            answer = call_llm(messages, ARK_API_KEY, model=ARK_MODEL)
            print(f"\n大模型回答:")
            print(f"  {answer}")
            
            if answer and "xxx" in answer:
                print(f"  ✓ 回答包含'xxx'，知识库生效！")
            else:
                print(f"  ✗ 回答未包含'xxx'，知识库可能未生效")
        else:
            print(f"  ⚠️  ARK_API_KEY未配置")
    except Exception as e:
        print(f"  ✗ 大模型调用失败: {e}")

    # 测试3: 调用API（模拟前端请求）
    print("\n【测试3: API完整流程】")
    try:
        api_url = "http://localhost:8001/api/question"
        payload = {
            "question": query,
            "ark_api_key": ARK_API_KEY or "",
            "model_id": ARK_MODEL,
            "kb_id": KB_ID or "",
            "kb_api_key": KB_API_KEY or "",
            "stream": False
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        print(f"API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('data', {}).get('answer', '')
            knowledge_used = result.get('data', {}).get('knowledge_used', False)
            
            print(f"\nAPI回答:")
            print(f"  {answer}")
            print(f"\n知识库使用: {'是' if knowledge_used else '否'}")
            
            if answer and "xxx" in answer:
                print(f"  ✓ API测试通过！知识库生效")
            else:
                print(f"  ✗ API测试失败！知识库未生效")
        else:
            print(f"  ✗ API请求失败: {response.text}")
    except requests.ConnectionError:
        print(f"  ⚠️  后端服务未启动，请先运行: bash start.sh backend")
    except Exception as e:
        print(f"  ✗ API调用失败: {e}")


def main():
    if len(sys.argv) < 2:
        print("用法: python test_kb.py <测试问题>")
        print("示例:")
        print("  python test_kb.py \"你叫什么？\"")
        print("  python test_kb.py \"你会什么？\"")
        print("  python test_kb.py \"介绍一下你自己\"")
        sys.exit(1)
    
    query = sys.argv[1]
    test_knowledge_base(query)


if __name__ == "__main__":
    main()
