import re
import time
from typing import Tuple, Dict

recent_questions: Dict[str, float] = {}
DEDUP_WINDOW_SECONDS = 30

# ============================================================
# M2: 面试领域术语词库 — ASR 常见误识别 → 正确术语
# ============================================================
TERM_CORRECTIONS: Dict[str, str] = {
    # 英文字母缩写（ASR 常识别为拼音/空格分隔）
    "热格": "RAG", "阿哥": "RAG", "rag": "RAG",
    "k 8 s": "Kubernetes", "k8 s": "Kubernetes", "k8s": "Kubernetes",
    "c i c d": "CI/CD", "c i": "CI", "c d": "CD",
    "a p i": "API", "e p i": "API",
    "a i": "AI", "g p u": "GPU", "c p u": "CPU",
    "g r p c": "gRPC", "grpc": "gRPC",
    "graph q l": "GraphQL", "graphql": "GraphQL",
    "rest full": "RESTful", "restful": "RESTful",
    "s a a s": "SaaS", "p a a s": "PaaS", "i a a s": "IaaS",
    "s s r": "SSR", "s s g": "SSG", "c s r": "CSR",
    "s q l": "SQL", "no sql": "NoSQL", "mysql": "MySQL",
    "h t t p": "HTTP", "h t t p s": "HTTPS",
    "j s o n": "JSON", "x m l": "XML", "y a m l": "YAML",
    "h t m l": "HTML", "c s s": "CSS", "d o m": "DOM",
    "o o p": "OOP", "m v c": "MVC", "m v v m": "MVVM",
    "t d d": "TDD", "d d d": "DDD",
    # 技术术语音近词
    "威武服务": "微服务",
    "容器话": "容器化",
    "德沃普斯": "DevOps", "低配": "DevOps", "devops": "DevOps",
    "单元侧试": "单元测试", "集成侧试": "集成测试",
    "抓娃": "Java", "java": "Java",
    "派森": "Python", "python": "Python",
    "够语言": "Go语言",
    "拉斯特": "Rust", "rust": "Rust",
    "卡夫卡": "Kafka", "kafka": "Kafka",
    "docker": "Docker", "道客": "Docker",
    "刀客": "Docker",
    "radies": "Redis", "radis": "Redis", "redis": "Redis",
    "芒狗 db": "MongoDB", "mongodb": "MongoDB",
    "post grace": "PostgreSQL", "postgresql": "PostgreSQL",
    "优拉夫": "Elasticsearch",
    "elasticsearch": "Elasticsearch",
    "耐克斯": "Nginx", "nginx": "Nginx",
    "杰肯斯": "Jenkins", "jenkins": "Jenkins",
    "吉他布": "GitLab", "gitlab": "GitLab",
    "吉他哈勃": "GitHub", "github": "GitHub",
    "li nux": "Linux", "linux": "Linux",
    "哈杜铺": "Hadoop", "hadoop": "Hadoop",
    "flink": "Flink",
    "spark": "Spark",
    "react": "React", "v u e": "Vue", "angela": "Angular",
    "type script": "TypeScript", "typescript": "TypeScript",
    "javascript": "JavaScript",
    "node js": "Node.js", "nodejs": "Node.js",
    "webpack": "Webpack", "vite": "Vite",
    # 面试场景常用语
    "store 法则": "STAR法则", "star 法则": "STAR法则",
    "行为面试": "行为面试", "技术面": "技术面",
    "系统设计": "系统设计",
}

# M3: 面试问题特征词
INTERVIEW_QUESTION_PATTERNS = [
    "怎么", "为什么", "说说", "介绍一下", "如何", "请讲", "请说",
    "谈谈", "看法", "经验", "遇到过", "怎么做", "能不能",
    "是什么", "什么是", "哪些", "哪种", "哪个",
    "了解", "熟悉", "掌握", "会吗", "知道", "做过", "用过",
    "介绍一下", "举例", "举例说明", "举个例子",
    "区别", "优缺点", "优势", "劣势", "好处", "缺点",
    "设计", "实现", "优化", "解决", "处理", "选择",
    "讲一下", "描述", "解释", "说明",
]


def correct_terms(text: str) -> Tuple[str, bool]:
    """M2: 纠正 ASR 常见术语误识别
    按词长降序替换。ASCII 词用 (?<![a-zA-Z])…(?![a-zA-Z]) 边界，
    防止匹配中文文本中嵌入的字母串内部。
    Returns: (corrected_text, was_corrected)
    """
    result = text
    corrected = False
    # 按 key 长度降序，长词优先
    sorted_terms = sorted(TERM_CORRECTIONS.items(), key=lambda x: len(x[0]), reverse=True)
    for wrong, correct in sorted_terms:
        if re.search(r'[a-zA-Z]', wrong):
            # ASCII/混合词：前后不能是字母（防止子串匹配）
            # 用 (?<![a-zA-Z]) 和 (?![a-zA-Z]) 替代 \\b，
            # 因为 \\b 在中文字符旁不生效（中文也是 \\w）
            pattern = r'(?<![a-zA-Z])' + re.escape(wrong) + r'(?![a-zA-Z])'
            if re.search(pattern, result):
                result = re.sub(pattern, correct, result)
                corrected = True
        else:
            # 纯中文：直接替换
            if wrong in result:
                result = result.replace(wrong, correct)
                corrected = True
    return result, corrected


def post_process_transcript(text: str, confidence: float = 1.0) -> Dict:
    """M2: 识别结果后处理管线
    Args:
        text: ASR 原始识别文本
        confidence: 语音识别置信度 (0.0-1.0)
    Returns:
        含原始文本、修正文本、置信度标记的字典
    """
    trimmed = text.strip()
    corrected_text, was_corrected = correct_terms(trimmed)

    return {
        "original": trimmed,
        "corrected": corrected_text,
        "confidence": confidence,
        "was_corrected": was_corrected,
        "low_confidence": confidence < 0.6,
    }


def is_interview_question(text: str) -> Tuple[bool, str]:
    """M3: 意图识别 — 判断文本是否是面试问题（而非闲聊/确认）
    Returns: (is_question, reason)
    """
    trimmed = text.strip()

    # 太短的不算问题
    if len(trimmed) < 4:
        return False, "文本过短"

    # 纯确认类/礼貌用语（不触发 LLM）
    confirm_only = {"好的", "嗯", "对", "是的", "可以", "行", "没问题", "好", "ok", "OK", "Ok"}
    if trimmed in confirm_only:
        return False, "确认类回复"

    # 疑问句特征
    if any(pattern in trimmed for pattern in INTERVIEW_QUESTION_PATTERNS):
        return True, "面试问题"

    # 以问号结尾
    if trimmed.endswith("?") or trimmed.endswith("？"):
        return True, "疑问句"

    # 长度足够 + 包含技术关键词 → 可能是面试陈述
    if len(trimmed) >= 8:
        return True, "长度足够"

    return False, "非问题"


def is_question(text: str) -> Tuple[bool, str]:
    if not text or text.strip() == '':
        return False, '空文本'

    trimmed = text.strip()

    if len(trimmed) <= 3:
        return False, '文本过短'

    return True, '有效语音'


def simple_similarity(a: str, b: str) -> float:
    shorter = a if len(a) < len(b) else b
    longer = b if len(a) < len(b) else a

    if len(shorter) == 0:
        return 0.0

    common_chars = 0
    longer_chars = set(longer)
    for char in shorter:
        if char in longer_chars:
            common_chars += 1

    return common_chars / len(longer)


def is_duplicate(text: str) -> bool:
    now = time.time()

    to_remove = []
    for key, timestamp in recent_questions.items():
        if now - timestamp > DEDUP_WINDOW_SECONDS:
            to_remove.append(key)

    for key in to_remove:
        del recent_questions[key]

    for existing in recent_questions:
        if simple_similarity(text, existing) > 0.7:
            return True

    recent_questions[text] = now
    return False


def validate_question(text: str, confidence: float = 1.0) -> Dict:
    """M2+M3: 增强版问题验证（含后处理 + 意图识别）
    Args:
        text: 原始识别文本
        confidence: ASR 置信度 (0.0-1.0)，默认 1.0 表示未知
    """
    if not text or text.strip() == '':
        return {
            'is_valid': False,
            'is_duplicate': False,
            'reason': '空文本',
            'rule': '',
            'corrected_text': '',
            'was_corrected': False,
        }

    # M2: 术语纠错
    corrected, was_corrected = correct_terms(text.strip())

    # M2: 低置信度标记（不拒绝，但标记供调用方决策）
    is_low_confidence = confidence < 0.6

    if len(corrected) <= 3:
        return {
            'is_valid': False,
            'is_duplicate': False,
            'reason': '文本过短',
            'rule': '',
            'corrected_text': corrected,
            'was_corrected': was_corrected,
        }

    # M3: 意图识别（非面试问题拒绝）
    is_interview, intent_reason = is_interview_question(corrected)
    if not is_interview:
        return {
            'is_valid': False,
            'is_duplicate': False,
            'reason': f'M3 意图过滤: {intent_reason}',
            'rule': intent_reason,
            'corrected_text': corrected,
            'was_corrected': was_corrected,
        }

    is_valid, rule = is_question(corrected)

    if is_duplicate(corrected):
        return {
            'is_valid': False,
            'is_duplicate': True,
            'reason': '重复问题',
            'rule': rule,
            'corrected_text': corrected,
            'was_corrected': was_corrected,
        }

    return {
        'is_valid': True,
        'is_duplicate': False,
        'reason': '',
        'rule': rule,
        'corrected_text': corrected,
        'was_corrected': was_corrected,
        'low_confidence': is_low_confidence,
    }