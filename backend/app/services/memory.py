"""面试会话记忆 — 检索结果缓存"""
import time
import logging
from typing import Dict, Optional

from config import SESSION_MEMORY_TTL, SESSION_MEMORY_MAX

logger = logging.getLogger("interview-tiger")


def simple_similarity(a: str, b: str) -> float:
    """简单字符级相似度（0.0-1.0）"""
    shorter = a if len(a) < len(b) else b
    longer = b if len(a) < len(b) else a
    if len(shorter) == 0:
        return 0.0
    longer_chars = set(longer)
    common = sum(1 for c in shorter if c in longer_chars)
    return common / len(longer)


class SessionMemory:
    """面试会话级检索缓存"""

    FOLLOW_UP_PATTERNS = [
        "还有呢", "继续说", "再详细", "比如说", "举个例子",
        "那", "另外", "除此", "具体", "能否展开",
    ]

    def __init__(self, ttl_seconds: int = SESSION_MEMORY_TTL,
                 max_sessions: int = SESSION_MEMORY_MAX):
        self._store: Dict[str, dict] = {}
        self._ttl = ttl_seconds
        self._max = max_sessions
        logger.info(f"[Memory] 会话记忆初始化 (TTL={ttl_seconds}s, max={max_sessions})")

    def _evict_expired(self):
        """清理过期条目"""
        now = time.time()
        expired = [
            sid for sid, v in self._store.items()
            if now - v.get("timestamp", 0) > self._ttl
        ]
        for sid in expired:
            del self._store[sid]
            logger.debug(f"[Memory] 过期清理 session={sid[:8]}")

    def get(self, session_id: str) -> Optional[dict]:
        """获取会话缓存，自动过期清理"""
        self._evict_expired()
        return self._store.get(session_id)

    def set(self, session_id: str, query: str, kb_results: str):
        """缓存检索结果"""
        self._evict_expired()
        # 超量淘汰：删除最老的
        if len(self._store) >= self._max and session_id not in self._store:
            oldest = min(self._store.items(), key=lambda x: x[1]["timestamp"])
            del self._store[oldest[0]]
        self._store[session_id] = {
            "query": query,
            "kb_results": kb_results,
            "timestamp": time.time(),
        }

    def is_follow_up(self, session_id: str, new_query: str) -> bool:
        """判断是否为跟进问题"""
        last = self.get(session_id)
        if not last:
            return False
        # 明确跟进关键词
        if any(p in new_query for p in self.FOLLOW_UP_PATTERNS):
            return True
        # 简单相似度 > 0.5
        if simple_similarity(new_query, last["query"]) > 0.5:
            return True
        return False
