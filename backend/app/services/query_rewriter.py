"""查询改写器 — 同义词扩展（复用 ASR 术语纠正词库）"""
import logging
from typing import List, Dict

logger = logging.getLogger("interview-tiger")

# 检索同义词词典（面试高频术语的同义/关联词扩展）
RETRIEVAL_SYNONYMS: Dict[str, List[str]] = {
    "微服务": ["微服务架构", "分布式服务", "服务化"],
    "数据库": ["SQL", "MySQL", "PostgreSQL", "数据存储", "NoSQL"],
    "面试": ["面试技巧", "STAR法则", "面试回答"],
    "项目管理": ["项目经验", "项目经历", "项目背景", "项目交付"],
    "前端": ["React", "Vue", "HTML", "CSS", "JavaScript", "TypeScript"],
    "后端": ["Java", "Python", "Go", "Node.js", "API", "RESTful"],
    "架构": ["系统设计", "技术架构", "架构设计", "分布式架构"],
    "高并发": ["性能优化", "并发编程", "多线程", "异步处理"],
    "缓存": ["Redis", "内存缓存", "缓存策略", "缓存穿透"],
    "消息队列": ["Kafka", "消息中间件", "异步通信", "削峰填谷"],
    "容器": ["Docker", "容器化", "Kubernetes", "K8s"],
    "监控": ["日志", "告警", "可观测性", "Prometheus", "链路追踪"],
    "安全": ["认证", "鉴权", "OAuth", "JWT", "SQL注入", "XSS"],
    "测试": ["单元测试", "集成测试", "TDD", "自动化测试", "性能测试"],
    "CI/CD": ["持续集成", "持续部署", "DevOps", "Jenkins", "流水线"],
}

MAX_EXPANSIONS = 3


class QueryRewriter:
    """查询改写器：同义词扩展 + 术语纠正"""

    def expand(self, query: str) -> List[str]:
        """将原始查询扩展为多个检索变体

        Args:
            query: 原始面试问题文本
        Returns:
            [原始query, 扩展变体...] 最多 MAX_EXPANSIONS 个
        """
        variants = [query]
        seen = {query}

        for term, synonyms in RETRIEVAL_SYNONYMS.items():
            if term in query:
                for syn in synonyms:
                    if syn not in seen and len(variants) < MAX_EXPANSIONS:
                        expanded = query.replace(term, syn)
                        if expanded not in seen:
                            variants.append(expanded)
                            seen.add(expanded)
        return variants
