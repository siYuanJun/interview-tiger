# 火山引擎方舟大模型调用服务
import json
import logging
from typing import Generator
import requests

from config import ARK_MODEL

logger = logging.getLogger("interview-tiger")

# 大模型API配置
LLM_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"


def call_llm(
    messages: list[dict],
    api_key: str,
    model: str = ARK_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    stream: bool = False
) -> str | None:
    """调用大模型（非流式）

    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        api_key: 火山引擎API Key (Bearer Token)
        model: 模型名称
        temperature: 温度参数 (0-1)
        max_tokens: 最大输出token数
        stream: 是否流式输出

    Returns:
        str: 模型生成的文本，失败返回 None
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }

    try:
        response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
            else:
                logger.warning(f"LLM返回格式异常: {result}")
                return None
        else:
            logger.error(f"LLM调用失败: HTTP {response.status_code} - {response.text[:200]}")
            return None
    except requests.Timeout:
        logger.error("LLM调用超时")
        return None
    except Exception as e:
        logger.error(f"LLM调用异常: {e}")
        return None


def call_llm_stream(
    messages: list[dict],
    api_key: str,
    model: str = ARK_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Generator[str, None, None]:
    """调用大模型（流式SSE）

    Args:
        messages: 消息列表
        api_key: 火山引擎API Key
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出token数

    Yields:
        str: 逐块生成的文本增量
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

    try:
        response = requests.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
            stream=True
        )

        if response.status_code != 200:
            logger.error(f"LLM流式调用失败: HTTP {response.status_code}")
            yield "[错误] 大模型调用失败，请检查API Key配置"
            return

        for chunk in response.iter_lines():
            if not chunk:
                continue
            chunk_str = chunk.decode('utf-8')
            if chunk_str.startswith('data: '):
                chunk_str = chunk_str[6:]
            if chunk_str == '[DONE]':
                break
            try:
                chunk_data = json.loads(chunk_str)
                if 'choices' in chunk_data and chunk_data['choices']:
                    delta = chunk_data['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        yield content
            except json.JSONDecodeError:
                pass

    except requests.Timeout:
        logger.error("LLM流式调用超时")
        yield "[错误] 请求超时，请稍后重试"
    except Exception as e:
        logger.error(f"LLM流式调用异常: {e}")
        yield "[错误] 服务异常，请稍后重试"
