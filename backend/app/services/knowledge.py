# 火山引擎知识库检索服务
import json
import requests

from app.utils.logger import logger, log_api_error

KB_API_URL = "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge"


def search_knowledge(
    query: str,
    kb_id: str,
    kb_api_key: str,
    project: str = "default",
    limit: int = 3,
    rerank: bool = True,
    retrieve_count: int = 25
) -> dict:
    payload = {
        'resource_id': kb_id,
        'project': project,
        'query': query,
        'limit': limit,
        'post_processing': {
            'rerank_switch': rerank,
            'retrieve_count': retrieve_count
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {kb_api_key}"
    }

    try:
        response = requests.post(KB_API_URL, headers=headers, json=payload, timeout=30)
        logger.info(f"search_knowledge - 状态码: {response.status_code}, KB_ID: {kb_id}, 响应体: {response.text[:500]}")
        if response.status_code == 200:
            return response.json()
        else:
            log_api_error("search_knowledge", Exception(f"HTTP {response.status_code}: {response.text[:200]}"), {"kb_id": kb_id, "query": query[:30]})
            return {}
    except Exception as e:
        log_api_error("search_knowledge", e, {"kb_id": kb_id, "query": query[:30]})
        return {}


def list_knowledge_bases(kb_api_key: str) -> dict:
    url = "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/list"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {kb_api_key}"
    }

    payload = {
        'project': 'default',
        'page_size': 20,
        'page_num': 1
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        logger.info(f"list_knowledge_bases - 状态码: {response.status_code}, 响应体: {response.text[:500]}")
        if response.status_code == 200:
            return response.json()
        else:
            log_api_error("list_knowledge_bases", Exception(f"HTTP {response.status_code}: {response.text[:200]}"), {"status": response.status_code})
            return {}
    except Exception as e:
        log_api_error("list_knowledge_bases", e, {})
        return {}


def get_relevant_knowledge(query: str, kb_id: str, kb_api_key: str) -> str:
    result = search_knowledge(query, kb_id, kb_api_key)

    knowledge = []
    if 'data' in result and 'result_list' in result['data']:
        for item in result['data']['result_list']:
            if 'content' not in item:
                continue
            score = item.get('score', 1.0)
            rerank_score = item.get('rerank_score', None)
            if rerank_score is not None:
                if float(rerank_score) < 0.3:
                    continue
            else:
                if float(score) < 0.05:
                    continue
            knowledge.append(item['content'])
            if len(knowledge) >= 3:
                break

    return '\n'.join(knowledge) if knowledge else ""
