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
1. 判断问题类型：确认类/技术类/行为类/其他
2. 确认类问题（如"能听到吗"、"准备好了吗"）：简短回答，1-2句话即可，直接回应
3. 技术类问题：结构化回答，采用STAR法则（情境-任务-行动-结果），重点突出
4. 行为类问题：结合实际经验，给出具体例子
5. 禁止客套话、废话、开场白（如"好的，针对..."、"这是一个专业问题"等）
6. 直接输出回答内容，不要包含分析、说明、注意事项等额外内容
7. 回答简洁直接，控制在50-200字

请直接生成回应建议："""

# 联网搜索Prompt模板（知识库无结果 + 开启联网搜索）
PROMPT_TEMPLATE_WITH_WEB_SEARCH = """你是一位资深的面试辅导专家。请针对以下面试官的话语，生成一个专业、简洁的回应建议。

【面试官话语】
{question}

【回答要求】
1. 判断问题类型：确认类/技术类/行为类/其他
2. 确认类问题：简短回答，1-2句话即可
3. 技术类问题：结构化回答，采用STAR法则，重点突出
4. 行为类问题：给出具体例子
5. 禁止客套话、废话、开场白
6. 直接输出回答内容，不要包含分析、说明、注意事项等额外内容
7. 回答简洁直接，控制在50-200字

请直接生成回应建议："""

# 降级Prompt模板（无知识库上下文）
PROMPT_TEMPLATE_WITHOUT_KNOWLEDGE = """你是一位资深的面试辅导专家。请针对以下面试官的话语，生成一个专业、简洁的回应建议。

【面试官话语】
{question}

【回答要求】
1. 判断问题类型：确认类/技术类/行为类/其他
2. 确认类问题：简短回答，1-2句话即可
3. 技术类问题：结构化回答，采用STAR法则，重点突出
4. 行为类问题：给出具体例子
5. 禁止客套话、废话、开场白
6. 直接输出回答内容，不要包含分析、说明、注意事项等额外内容
7. 回答简洁直接，控制在50-200字

请直接生成回应建议："""


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
