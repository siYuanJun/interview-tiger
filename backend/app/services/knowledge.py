# 火山引擎知识库检索服务
import json
import logging
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

logger = logging.getLogger("interview-tiger")

# 知识库API配置
KB_API_URL = "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge"
KB_API_HOST = "api-knowledgebase.mlp.cn-beijing.volces.com"
KB_SERVICE = "air"
KB_REGION = "cn-north-1"


def _sign_request(method: str, path: str, ak: str, sk: str, data: dict = None) -> tuple:
    """使用 SignerV4 签名请求

    Args:
        method: HTTP 方法
        path: 请求路径
        ak: Access Key
        sk: Secret Key
        data: 请求体 dict

    Returns:
        (headers, body) 签名后的请求头和请求体
    """
    r = Request()
    r.set_shema("https")
    r.set_method(method)
    r.set_connection_timeout(10)
    r.set_socket_timeout(10)

    mheaders = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Host": KB_API_HOST
    }
    r.set_headers(mheaders)
    r.set_host(KB_API_HOST)
    r.set_path(path)

    if data is not None:
        r.set_body(json.dumps(data))

    credentials = Credentials(ak, sk, KB_SERVICE, KB_REGION)
    SignerV4.sign(r, credentials)

    return r.headers, r.body


def search_knowledge(
    query: str,
    kb_id: str,
    kb_api_key: str,
    project: str = "default",
    limit: int = 3,
    rerank: bool = True,
    retrieve_count: int = 25
) -> dict:
    """搜索知识库

    Args:
        query: 检索查询文本
        kb_id: 知识库ID (如 kb-xxx)
        kb_api_key: AK:SK 格式的API Key
        project: 项目名称
        limit: 返回结果数量上限
        rerank: 是否开启重排序
        retrieve_count: 初检召回数量

    Returns:
        dict: API原始响应
    """
    # 拆解 AK:SK
    if ':' in kb_api_key:
        ak, sk = kb_api_key.split(':', 1)
    else:
        logger.warning("知识库API Key格式不正确，期望 AK:SK 格式")
        return {}

    path = '/api/knowledge/collection/search_knowledge'

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

    try:
        headers, body = _sign_request('POST', path, ak, sk, payload)
        response = requests.post(KB_API_URL, headers=headers, data=body, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"知识库检索失败: HTTP {response.status_code} - {response.text[:200]}")
            return {}
    except Exception as e:
        logger.error(f"知识库检索异常: {e}")
        return {}


def get_relevant_knowledge(query: str, kb_id: str, kb_api_key: str) -> str:
    """获取相关知识内容（已过滤低相关性结果）

    Args:
        query: 检索查询文本
        kb_id: 知识库ID
        kb_api_key: AK:SK 格式的API Key

    Returns:
        str: 拼接后的知识内容，无结果返回空字符串
    """
    result = search_knowledge(query, kb_id, kb_api_key)

    knowledge = []
    if 'data' in result and 'result_list' in result['data']:
        for item in result['data']['result_list']:
            if 'content' not in item:
                continue
            score = item.get('score', 1.0)
            rerank_score = item.get('rerank_score', score)
            # 过滤低相关性结果（rerank_score < 0.3）
            if float(rerank_score) < 0.3:
                continue
            knowledge.append(item['content'])
            if len(knowledge) >= 3:
                break

    return '\n'.join(knowledge) if knowledge else ""
