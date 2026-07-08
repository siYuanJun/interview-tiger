from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import json
import requests

from app.utils.logger import logger, log_api_error
from config import KB_BASE_URL, KB_PROJECT


class KnowledgeProvider(ABC):
    @abstractmethod
    def search(self, query: str, **kwargs) -> str:
        pass

    @abstractmethod
    def search_with_details(self, query: str, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def upload(self, files, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def list_docs(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_doc(self, doc_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def clear(self) -> Dict[str, Any]:
        pass


class VolcengineKnowledgeProvider(KnowledgeProvider):
    def __init__(self, kb_id: Optional[str] = None, kb_api_key: Optional[str] = None):
        self.kb_id = kb_id
        self.kb_api_key = kb_api_key

    def _search_knowledge(
        self,
        query: str,
        kb_id: str,
        kb_api_key: str,
        project: str = KB_PROJECT,
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
            response = requests.post(KB_BASE_URL, headers=headers, json=payload, timeout=30)
            logger.info(f"search_knowledge - 状态码: {response.status_code}, KB_ID: {kb_id}, 响应体: {response.text[:500]}")
            if response.status_code == 200:
                return response.json()
            else:
                # 检测授权错误，给出明确提示
                resp_text = response.text[:200]
                if "check sign error" in resp_text or response.status_code == 403:
                    logger.error(f"火山引擎知识库鉴权失败！请检查 KB_API_KEY 是否为有效的 Bearer Token（非 AK:SK 格式）")
                log_api_error("search_knowledge", Exception(f"HTTP {response.status_code}: {resp_text}"), {"kb_id": kb_id, "query": query[:30]})
                return {}
        except Exception as e:
            log_api_error("search_knowledge", e, {"kb_id": kb_id, "query": query[:30]})
            return {}

    def search(self, query: str, **kwargs) -> str:
        kb_id = kwargs.get('kb_id', self.kb_id)
        kb_api_key = kwargs.get('kb_api_key', self.kb_api_key)
        
        if not kb_id or not kb_api_key:
            logger.warning("火山引擎知识库配置不完整")
            return ""

        result = self._search_knowledge(query, kb_id, kb_api_key)

        knowledge = []
        if 'data' in result and 'result_list' in result['data']:
            for item in result['data']['result_list']:
                if 'content' not in item:
                    continue
                score = item.get('score', 1.0)
                rerank_score = item.get('rerank_score', None)
                if rerank_score is not None:
                    if float(rerank_score) < 0.02:
                        continue
                else:
                    if float(score) < 0.02:
                        continue
                knowledge.append(item['content'])
                if len(knowledge) >= 3:
                    break

        return '\n'.join(knowledge) if knowledge else ""

    def search_with_details(self, query: str, **kwargs) -> Dict[str, Any]:
        kb_id = kwargs.get('kb_id', self.kb_id)
        kb_api_key = kwargs.get('kb_api_key', self.kb_api_key)
        
        if not kb_id or not kb_api_key:
            logger.warning("火山引擎知识库配置不完整")
            return {"chunks": []}

        result = self._search_knowledge(query, kb_id, kb_api_key)

        chunks = []
        if 'data' in result and 'result_list' in result['data']:
            for item in result['data']['result_list']:
                if 'content' not in item:
                    continue
                score = item.get('score', 1.0)
                rerank_score = item.get('rerank_score', None)
                if rerank_score is not None:
                    if float(rerank_score) < 0.02:
                        continue
                else:
                    if float(score) < 0.02:
                        continue
                chunks.append({
                    "content": item['content'],
                    "score": float(rerank_score) if rerank_score else float(score),
                    "doc_name": item.get('source', '知识库文档'),
                    "doc_id": item.get('id', '')
                })
                if len(chunks) >= 5:
                    break

        return {"chunks": chunks}

    def upload(self, files, **kwargs) -> Dict[str, Any]:
        return {"code": 0, "message": "火山引擎知识库不支持通过此接口上传，请在控制台操作", "data": []}

    def list_docs(self) -> List[Dict[str, Any]]:
        return []

    def delete_doc(self, doc_id: str) -> Dict[str, Any]:
        return {"code": 0, "message": "火山引擎知识库不支持通过此接口删除，请在控制台操作", "data": {}}

    def clear(self) -> Dict[str, Any]:
        return {"code": 0, "message": "火山引擎知识库不支持通过此接口清空，请在控制台操作", "data": {}}


def get_relevant_knowledge(query: str, kb_id: str, kb_api_key: str) -> str:
    provider = VolcengineKnowledgeProvider(kb_id, kb_api_key)
    return provider.search(query)
