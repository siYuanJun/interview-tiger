// 问题判断工具 - TASK-013
// 判断识别出的文本是否为面试官有效提问

// 疑问语气词结尾
const QUESTION_MARKS = ['？', '?', '吗', '呢', '吧']

// 疑问词
const QUESTION_WORDS = [
  '什么', '怎么', '为什么', '如何', '哪', '谁', '多少',
  '几个', '是否', '能不能', '可以', '请问', '我想问',
  '能说一下', '介绍', '谈谈', '聊聊', '说说', '描述',
  '列举', '讲一下', '说一下', '解释', '阐述'
]

// 典型提问句式开头
const QUESTION_PATTERNS = [
  '请问', '我想问', '想问一下', '能说一下', '能不能',
  '可以吗', '方便吗', '怎么样', '怎么看', '如何看'
]

// 去重记录
const recentQuestions: Map<string, number> = new Map()
const DEDUP_WINDOW_MS = 30000 // 30秒去重窗口

/**
 * 判断文本是否为面试官有效提问
 */
export function isQuestion(text: string): boolean {
  if (!text || text.trim().length === 0) return false

  const trimmed = text.trim()

  // 规则1: 长度过滤（过滤语气词和无效语音）
  if (trimmed.length <= 3) return false

  // 规则2: 标点符号规则
  if (QUESTION_MARKS.some(mark => trimmed.endsWith(mark))) {
    return true
  }

  // 规则3: 疑问词规则
  if (QUESTION_WORDS.some(word => trimmed.includes(word))) {
    return true
  }

  // 规则4: 句式规则
  if (QUESTION_PATTERNS.some(pattern => trimmed.startsWith(pattern))) {
    return true
  }

  return false
}

/**
 * 计算两个字符串的简单相似度（基于公共子串比例）
 */
function simpleSimilarity(a: string, b: string): number {
  const shorter = a.length < b.length ? a : b
  const longer = a.length < b.length ? b : a

  if (shorter.length === 0) return 0

  let commonChars = 0
  for (const char of shorter) {
    if (longer.includes(char)) {
      commonChars++
    }
  }
  return commonChars / longer.length
}

/**
 * 检查问题是否在去重窗口内重复
 */
export function isDuplicateQuestion(text: string): boolean {
  const now = Date.now()

  // 清理过期记录
  for (const [key, timestamp] of recentQuestions.entries()) {
    if (now - timestamp > DEDUP_WINDOW_MS) {
      recentQuestions.delete(key)
    }
  }

  // 检查相似度
  for (const [existing, _] of recentQuestions.entries()) {
    const similarity = simpleSimilarity(text, existing)
    if (similarity > 0.7) {
      return true
    }
  }

  // 记录当前问题
  recentQuestions.set(text, now)
  return false
}

/**
 * 综合判断：是否为有效问题 + 是否重复
 */
export function validateQuestion(text: string): {
  isValid: boolean
  isDuplicate: boolean
  reason: string
} {
  if (!text || text.trim().length === 0) {
    return { isValid: false, isDuplicate: false, reason: '空文本' }
  }

  if (text.trim().length <= 3) {
    return { isValid: false, isDuplicate: false, reason: '文本过短' }
  }

  if (!isQuestion(text)) {
    return { isValid: false, isDuplicate: false, reason: '非疑问句' }
  }

  if (isDuplicateQuestion(text)) {
    return { isValid: false, isDuplicate: true, reason: '重复问题' }
  }

  return { isValid: true, isDuplicate: false, reason: '' }
}
