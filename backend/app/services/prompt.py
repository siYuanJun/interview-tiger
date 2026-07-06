# Prompt拼接服务
import logging

logger = logging.getLogger("interview-tiger")

# 标准Prompt模板（有知识库上下文）
PROMPT_TEMPLATE_WITH_KNOWLEDGE = """你是一位资深的面试辅导专家。请根据以下信息，为求职者生成一个针对面试官话语的回应建议。

【求职者背景信息】
{knowledge_context}

【面试官话语】
{question}

【回答要求】
1. 判断面试官的意图：可能是提问、陈述、评价、要求等，根据不同意图给出合适的回应策略
2. 如果是问题，回答要结合求职者的真实背景，体现个人特色，不要使用通用模板
3. 如果是陈述或评价，给出恰当的回应方式（如表示感谢、确认理解、补充说明等）
4. 如果是要求，给出如何满足要求的建议
5. 回答结构清晰（可采用STAR法则：情境-任务-行动-结果）
6. 语气自信、专业、诚恳
7. 回答时长控制在1-3分钟（约200-500字）

请生成回应建议："""

# 联网搜索Prompt模板（知识库无结果 + 开启联网搜索）
PROMPT_TEMPLATE_WITH_WEB_SEARCH = """你是一位资深的面试辅导专家。知识库中暂无该求职者的背景资料，但你可以通过联网搜索获取行业通用知识来辅助回答。

请针对以下面试官的话语，生成一个专业、结构清晰的回应建议。

【面试官话语】
{question}

【回答要求】
1. 判断面试官的意图：可能是提问、陈述、评价、要求等，根据不同意图给出合适的回应策略
2. 基于面试岗位的行业通用要求，给出专业建议
3. 如果是问题，采用STAR法则组织回答框架
4. 如果是陈述或评价，给出恰当的回应方式
5. 结合行业常见面试关注点，提供有针对性的回应思路
6. 语气自信、诚恳
7. 回答时长控制在1-3分钟（约200-500字）

请生成回应建议："""

# 降级Prompt模板（无知识库上下文）
PROMPT_TEMPLATE_WITHOUT_KNOWLEDGE = """你是一位资深的面试辅导专家。请针对以下面试官的话语，生成一个专业、结构清晰的回应建议。

【面试官话语】
{question}

【回答要求】
1. 判断面试官的意图：可能是提问、陈述、评价、要求等，根据不同意图给出合适的回应策略
2. 如果是问题，回答要专业、有逻辑、体现思考深度，采用STAR法则组织回答
3. 如果是陈述或评价，给出恰当的回应方式
4. 语气自信、诚恳
5. 回答时长控制在1-3分钟（约200-500字）

请生成回应建议："""


def build_prompt(question: str, knowledge_context: str = "", use_web_search: bool = False) -> str:
    """构建发送给大模型的完整Prompt

    Args:
        question: 面试官提出的问题
        knowledge_context: 知识库检索到的个人背景信息
        use_web_search: 是否开启联网搜索（知识库无结果时的降级方案）

    Returns:
        str: 拼接好的完整Prompt
    """
    if knowledge_context and knowledge_context.strip():
        logger.info("使用知识库增强Prompt")
        return PROMPT_TEMPLATE_WITH_KNOWLEDGE.format(
            knowledge_context=knowledge_context.strip(),
            question=question.strip()
        )
    elif use_web_search:
        logger.info("知识库无匹配，启用联网搜索模式")
        return PROMPT_TEMPLATE_WITH_WEB_SEARCH.format(
            question=question.strip()
        )
    else:
        logger.info("使用无知识库降级Prompt")
        return PROMPT_TEMPLATE_WITHOUT_KNOWLEDGE.format(
            question=question.strip()
        )


def build_messages(question: str, knowledge_context: str = "", use_web_search: bool = False) -> list[dict]:
    """构建Chat Completions格式的消息列表

    Args:
        question: 面试官问题
        knowledge_context: 知识库检索结果
        use_web_search: 是否开启联网搜索

    Returns:
        list[dict]: messages列表
    """
    prompt = build_prompt(question, knowledge_context, use_web_search)
    return [{"role": "user", "content": prompt}]
