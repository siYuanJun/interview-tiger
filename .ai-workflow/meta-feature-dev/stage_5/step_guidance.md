# Stage 5: 分步指导 — M1 断句端点检测优化

## 依赖关系图

```
Step 1 (新增常量+变量)
  ↓
Step 2 (实现辅助函数)
  ↓
Step 3 (重构 onresult 断句逻辑)
  ↓
Step 4 (清理逻辑更新)
  ↓
Step 5 (本地验证)
```

---

## Step 1: 新增常量与运行时变量

**文件**: `frontend/src/composables/useSpeech.ts`

**操作**:
- 在现有 `pauseTimer` 声明区域（第 22-24 行附近）新增变量
- 新增常量定义（放在函数体顶部，`isListening` 等 ref 声明之后）

**变更**:
```typescript
// 新增常量（放在函数体顶部）
const SHORT_TIMEOUT_MS = 800
const LONG_TIMEOUT_MS = 2500
const CONFIDENCE_THRESHOLD = 0.7
const MIN_TEXT_LENGTH = 5
const REMARK_WINDOW_SIZE = 5
const SENTENCE_ENDINGS = new Set(['。', '！', '？', '…', '!', '?'])

// 新增运行时变量（放在 pauseTimer 声明旁）
let shortTimer: ReturnType<typeof setTimeout> | null = null
let longTimer: ReturnType<typeof setTimeout> | null = null
let remarkWindow: Array<{ time: number; chars: number }> = []
let lastConfidence = 0
```

**验收标准**:
- [ ] `tsc --noEmit` 无类型错误
- [ ] 变量命名不与现有冲突

---

## Step 2: 实现辅助函数

**文件**: `frontend/src/composables/useSpeech.ts`

**操作**: 在 `getErrorMessage()` 函数之后（第 213 行附近），新增 4 个辅助函数

**变更**:
```typescript
function calculateSpeechRate(): number {
  if (remarkWindow.length < 2) return 5 // 默认正常语速
  const first = remarkWindow[0]
  const last = remarkWindow[remarkWindow.length - 1]
  const duration = (last.time - first.time) / 1000
  if (duration <= 0) return 5
  const totalChars = remarkWindow.reduce((sum, r) => sum + r.chars, 0)
  return totalChars / duration
}

function hasSentenceEnding(text: string): boolean {
  if (!text) return false
  const lastChar = text[text.length - 1]
  return SENTENCE_ENDINGS.has(lastChar)
}

function shouldPauseEarly(): boolean {
  const text = currentText.value.trim()
  if (!text || text.length < MIN_TEXT_LENGTH) return false
  if (hasSentenceEnding(text)) return true
  if (lastConfidence > CONFIDENCE_THRESHOLD && text.length > 10) return true
  return false
}

function clearTimers() {
  if (shortTimer) { clearTimeout(shortTimer); shortTimer = null }
  if (longTimer) { clearTimeout(longTimer); longTimer = null }
}
```

**验收标准**:
- [ ] `calculateSpeechRate()` 空窗口返回默认值 5
- [ ] `hasSentenceEnding('你好。')` 返回 true
- [ ] `hasSentenceEnding('你好')` 返回 false
- [ ] `shouldPauseEarly()` 在无文本时返回 false

---

## Step 3: 重构 onresult 断句逻辑（核心步骤）

**文件**: `frontend/src/composables/useSpeech.ts`

**操作**: 替换第 100-113 行的 pauseTimer 逻辑块

**Before** (L100-113):
```typescript
if (interimText) {
  currentText.value = interimText
  state.value = 'recognizing'
  
  if (pauseTimer) clearTimeout(pauseTimer)
  pauseTimer = setTimeout(() => {
    if (generation !== currentGeneration) return
    if (isListening.value && currentText.value.trim()) {
      const pausedResult = pauseRecognition()
      if (pausedResult) {
        options.onResult?.(pausedResult)
      }
    }
  }, 1500)
}
```

**After**:
```typescript
if (interimText) {
  currentText.value = interimText
  state.value = 'recognizing'
  
  // 语速跟踪：记录本次 interim 的时间戳和字符数
  remarkWindow.push({ time: Date.now(), chars: interimText.length })
  if (remarkWindow.length > REMARK_WINDOW_SIZE) remarkWindow.shift()
  
  // 记录最后一次置信度
  const lastResult = event.results[event.results.length - 1]
  if (lastResult?.[0]?.confidence) {
    lastConfidence = lastResult[0].confidence
  }
  
  // 双定时器策略
  clearTimers()
  
  if (currentText.value.trim().length >= MIN_TEXT_LENGTH) {
    shortTimer = setTimeout(() => {
      if (generation !== currentGeneration) return
      if (isListening.value && shouldPauseEarly()) {
        const result = pauseRecognition()
        if (result) options.onResult?.(result)
      }
    }, SHORT_TIMEOUT_MS)
    
    longTimer = setTimeout(() => {
      if (generation !== currentGeneration) return
      if (isListening.value && currentText.value.trim()) {
        const result = pauseRecognition()
        if (result) options.onResult?.(result)
      }
    }, LONG_TIMEOUT_MS)
  }
}
```

**验收标准**:
- [ ] interim 文本出现后，shortTimer 和 longTimer 同时启动
- [ ] 句末标点触发 shortTimer 立即断句
- [ ] 无句末标点时，高置信度 (>0.7) 在 shortTimer 到期后断句
- [ ] longTimer 到期后无论置信度如何都强制断句
- [ ] `generation` 不匹配时不触发断句（防止过期回调）

---

## Step 4: 清理逻辑更新

**文件**: `frontend/src/composables/useSpeech.ts`

**操作**: 在 `stopListening()` 函数（第 216 行）中，于 `pauseTimer` 清理代码后增加双定时器清理

**变更**:
```typescript
// 在 stopListening() 中，if (pauseTimer) { ... } 块之后新增：
clearTimers()
remarkWindow = []
lastConfidence = 0
```

**验收标准**:
- [ ] 调用 `stopListening()` 后，shortTimer 和 longTimer 均为 null
- [ ] remarkWindow 被清空
- [ ] 下次 `startListening()` 不会携带上次的语速历史

---

## Step 5: 本地构建验证

**操作**:
```bash
cd frontend && npm run build
```

**验收标准**:
- [ ] `npm run build` 无错误
- [ ] `npm run type-check` (如有) 无类型错误
- [ ] 项目可正常启动 (`npm run dev`)

---

## 步骤汇总

| Step | 改动量 | 改动区域 | 风险 |
|:----:|:------:|---------|:----:|
| 1 | ~10 行 | 变量声明区 | 🟢 |
| 2 | ~35 行 | 新函数区 | 🟢 |
| 3 | ~25 行替换 | onresult 回调 | 🟡 |
| 4 | ~3 行 | stopListening | 🟢 |
| 5 | 0 行 | 构建验证 | 🟢 |

**总计**: ~50 行新增 + ~10 行替换，1 个文件

## 门控状态

- [x] `steps_decomposed` — 5 个独立步骤
- [x] `acceptance_criteria_per_step` — 每步 2-4 条验收标准
- [x] `dependency_order_defined` — 线性依赖链
