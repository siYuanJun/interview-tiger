# 火山引擎方舟大模型调用服务
import json
from typing import Generator
import requests

from config import ARK_MODEL, WEB_SEARCH_BOT_ID
from app.utils.logger import logger, log_api_error

# 大模型API配置
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
LLM_API_URL = f"{ARK_BASE_URL}/chat/completions"
# Bot应用端点（用于联网搜索）
BOT_API_URL = f"{ARK_BASE_URL}/bots/chat/completions"


def call_llm(
    messages: list[dict],
    api_key: str,
    model: str = ARK_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    stream: bool = False,
    enable_search: bool = False
) -> str | None:
    """调用大模型（非流式）

    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        api_key: 火山引擎API Key (Bearer Token)
        model: 模型名称
        temperature: 温度参数 (0-1)
        max_tokens: 最大输出token数
        stream: 是否流式输出
        enable_search: 是否开启联网搜索

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

    # 联网搜索：优先使用 Bot 端点，否则添加 enable_search 参数
    api_url = LLM_API_URL
    if enable_search:
        if WEB_SEARCH_BOT_ID:
            # 使用 Bot 应用端点（需在控制台创建Bot并开通联网插件）
            api_url = BOT_API_URL
            payload["model"] = WEB_SEARCH_BOT_ID
            logger.info(f"联网搜索启用 (Bot模式): {WEB_SEARCH_BOT_ID}")
        else:
            # 尝试通过 enable_search 参数开启
            payload["enable_search"] = True
            logger.info("联网搜索启用 (enable_search参数)")

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
            else:
                logger.warning(f"LLM返回格式异常: {result}")
                return None
        else:
            log_api_error("call_llm", Exception(f"HTTP {response.status_code}"), {"model": model, "status": response.status_code})
            return None
    except requests.Timeout:
        log_api_error("call_llm", Exception("超时"), {"model": model})
        return None
    except Exception as e:
        log_api_error("call_llm", e, {"model": model})
        return None


def call_llm_stream(
    messages: list[dict],
    api_key: str,
    model: str = ARK_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    enable_search: bool = False
) -> Generator[str, None, None]:
    """调用大模型（流式SSE）

    Args:
        messages: 消息列表
        api_key: 火山引擎API Key
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出token数
        enable_search: 是否开启联网搜索

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

    # 联网搜索：优先使用 Bot 端点，否则添加 enable_search 参数
    api_url = LLM_API_URL
    if enable_search:
        if WEB_SEARCH_BOT_ID:
            api_url = BOT_API_URL
            payload["model"] = WEB_SEARCH_BOT_ID
            logger.info(f"联网搜索启用 (Bot模式) [stream]: {WEB_SEARCH_BOT_ID}")
        else:
            payload["enable_search"] = True
            logger.info("联网搜索启用 (enable_search参数) [stream]")

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60 if enable_search else 30,  # 联网搜索增加超时
            stream=True
        )

        if response.status_code != 200:
            log_api_error("call_llm_stream", Exception(f"HTTP {response.status_code}"), {"model": model})
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
        log_api_error("call_llm_stream", Exception("超时"), {"model": model})
        yield "[错误] 请求超时，请稍后重试"
    except Exception as e:
        log_api_error("call_llm_stream", e, {"model": model})
        yield "[错误] 服务异常，请稍后重试"
