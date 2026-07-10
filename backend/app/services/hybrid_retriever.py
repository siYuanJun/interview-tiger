"""BM25 + Dense 混合检索器（RRF 融合）"""
import logging
from typing import List, Optional

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from config import BM25_WEIGHT

logger = logging.getLogger("interview-tiger")

# jieba 为可选依赖（Docker 中未安装时降级为简单分词）
try:
    import jieba
    _JIEBA_AVAILABLE = True
except ImportError:
    jieba = None
    _JIEBA_AVAILABLE = False


def hybrid_tokenize(text: str) -> List[str]:
    """jieba 中文分词（如不可用则按字符切分）"""
    if _JIEBA_AVAILABLE:
        tokens = jieba.lcut(text)
        return [t.strip() for t in tokens if t.strip()]
    # 降级：按空格和常见标点切分
    import re
    tokens = re.split(r'[\s,，。！？；：、]+', text)
    return [t.strip() for t in tokens if t.strip()]


class HybridRetriever:
    """BM25 + Dense 向量混合检索器"""

    def __init__(self, vector_store: Chroma, all_documents: List[Document]):
        self._ready = False
        try:
            self.vector_retriever = vector_store.as_retriever(
                search_kwargs={"k": 5}
            )
            self.bm25_retriever = BM25Retriever.from_documents(
                all_documents,
                preprocess_func=hybrid_tokenize
            )
            self.bm25_retriever.k = 5
            self.ensemble = EnsembleRetriever(
                retrievers=[self.bm25_retriever, self.vector_retriever],
                weights=[BM25_WEIGHT, 1.0 - BM25_WEIGHT]
            )
            self._ready = True
            logger.info(f"[Hybrid] 混合检索器初始化成功 (BM25权重={BM25_WEIGHT})")
        except Exception as e:
            logger.warning(f"[Hybrid] BM25 初始化失败，回退纯向量检索: {e}")
            self.vector_retriever = None
            if vector_store:
                self.vector_retriever = vector_store.as_retriever(
                    search_kwargs={"k": 5}
                )

    def is_ready(self) -> bool:
        return self._ready

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """执行混合检索"""
        if self._ready:
            try:
                docs = self.ensemble.invoke(query)
                return docs[:top_k]
            except Exception as e:
                logger.warning(f"[Hybrid] 混合检索异常，回退: {e}")
        # 降级：纯向量检索
        if self.vector_retriever:
            return self.vector_retriever.invoke(query)[:top_k]
        return []
