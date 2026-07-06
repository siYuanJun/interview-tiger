import time
from typing import Tuple, Dict

recent_questions: Dict[str, float] = {}
DEDUP_WINDOW_SECONDS = 30


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