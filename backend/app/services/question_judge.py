import time
from typing import Tuple, Dict

QUESTION_MARKS = ['？', '?', '吗', '呢', '吧']

QUESTION_WORDS = [
    '什么', '怎么', '为什么', '如何', '哪', '谁', '多少',
    '几个', '是否', '能不能', '可以', '请问', '我想问',
    '能说一下', '介绍', '谈谈', '聊聊', '说说', '描述',
    '列举', '讲一下', '说一下', '解释', '阐述', '会不会', '好不好'
]

QUESTION_PATTERNS = [
    '请问', '我想问', '想问一下', '能说一下', '能不能',
    '可以吗', '方便吗', '怎么样', '怎么看', '如何看', '是吧'
]

recent_questions: Dict[str, float] = {}
DEDUP_WINDOW_SECONDS = 30


def is_question(text: str) -> Tuple[bool, str]:
    if not text or text.strip() == '':
        return False, '空文本'

    trimmed = text.strip()

    if len(trimmed) <= 3:
        return False, '文本过短'

    if any(mark in trimmed[-2:] for mark in QUESTION_MARKS):
        return True, '标点规则'

    if any(word in trimmed for word in QUESTION_WORDS):
        return True, '疑问词规则'

    if any(trimmed.startswith(pattern) for pattern in QUESTION_PATTERNS):
        return True, '句式规则'

    return False, '非疑问句'


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


def validate_question(text: str) -> Dict:
    if not text or text.strip() == '':
        return {
            'is_valid': False,
            'is_duplicate': False,
            'reason': '空文本',
            'rule': ''
        }

    trimmed = text.strip()

    if len(trimmed) <= 3:
        return {
            'is_valid': False,
            'is_duplicate': False,
            'reason': '文本过短',
            'rule': ''
        }

    is_valid, rule = is_question(trimmed)
    if not is_valid:
        return {
            'is_valid': False,
            'is_duplicate': False,
            'reason': '非疑问句',
            'rule': ''
        }

    if is_duplicate(trimmed):
        return {
            'is_valid': False,
            'is_duplicate': True,
            'reason': '重复问题',
            'rule': rule
        }

    return {
        'is_valid': True,
        'is_duplicate': False,
        'reason': '',
        'rule': rule
    }