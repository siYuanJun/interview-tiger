// 语音输入验证工具 - TASK-013
// 验证识别出的文本是否为有效的语音输入（非噪声）

// 去重记录
const recentQuestions: Map<string, number> = new Map()
const DEDUP_WINDOW_MS = 30000 // 30秒去重窗口

/**
 * 判断文本是否为有效的语音输入
 */
export function isQuestion(text: string): boolean {
  if (!text || text.trim().length === 0) return false

  const trimmed = text.trim()

  if (trimmed.length <= 3) return false

  return true
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
 * 综合判断：是否为有效语音输入 + 是否重复
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

  if (isDuplicateQuestion(text)) {
    return { isValid: false, isDuplicate: true, reason: '重复问题' }
  }

  return { isValid: true, isDuplicate: false, reason: '' }
}
