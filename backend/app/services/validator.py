"""检索结果校验器 — LLM 批量判断片段相关性"""
import asyncio
import logging
from typing import List

from config import ARK_MODEL, ARK_API_KEY, VALIDATOR_TIMEOUT

logger = logging.getLogger("interview-tiger")

VALIDATOR_PROMPT = """你是一个检索结果相关性判断器。
对于以下每个编号的文本片段，判断它是否与面试问题相关。
只回答 YES 或 NO，不要解释。

面试问题: {question}

{chunks}

请按编号输出：
"""


class ContentValidator:
    """用 LLM 批量判断检索片段是否与问题相关"""

    def __init__(self, model_id: str = ARK_MODEL, api_key: str = ARK_API_KEY):
        self.model = model_id
        self.api_key = api_key
        self.timeout = VALIDATOR_TIMEOUT
        self._enabled = bool(api_key)

    def is_enabled(self) -> bool:
        return self._enabled

    def validate(self, question: str, chunks: List[str]) -> List[str]:
        """批量校验：返回通过校验的相关片段

        Args:
            question: 面试问题
            chunks: 检索到的文档片段列表
        Returns:
            通过校验的相关片段（校验失败/超时时返回全量）
        """
        if not chunks or not self._enabled:
            return chunks

        # 构建批量判断 Prompt
        numbered = "\n".join(
            f"[{i + 1}] {chunk[:300]}"
            for i, chunk in enumerate(chunks)
        )
        prompt = VALIDATOR_PROMPT.format(question=question, chunks=numbered)

        try:
            # 同步调用 LLM（在 search() 的 asyncio.to_thread 中执行）
            from app.services.llm import call_llm
            response = call_llm(
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key,
                model=self.model,
                temperature=0.0,
                max_tokens=200
            )

            if not response:
                logger.warning("[Validator] LLM 返回空，保留全部片段")
                return chunks

            # 解析 YES/NO
            valid_indices = set()
            for line in response.strip().split("\n"):
                line = line.strip()
                if "YES" in line.upper():
                    # 提取编号
                    for i in range(len(chunks)):
                        if f"[{i + 1}]" in line or str(i + 1) in line:
                            valid_indices.add(i)

            if not valid_indices:
                # 解析失败，保留全部
                logger.warning(f"[Validator] 解析失败，保留全部 {len(chunks)} 片段")
                return chunks

            filtered = [chunks[i] for i in range(len(chunks)) if i in valid_indices]
            logger.info(
                f"[Validator] {len(chunks)} → {len(filtered)} 片段 "
                f"(过滤 {len(chunks) - len(filtered)} 个无关)"
            )
            return filtered

        except Exception as e:
            logger.warning(f"[Validator] 异常，跳过校验: {e}")
            return chunks
