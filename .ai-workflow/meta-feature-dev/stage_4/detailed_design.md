# Stage 4: 详细设计 — M1 断句端点检测优化

## 技术架构

```
┌──────────────────────────────────────────────────────────┐
│                    useSpeech.ts                           │
│  startListening() → rec.onresult                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │          断句决策引擎（新）                        │    │
│  │                                                  │    │
│  │  interim 事件 →                                   │    │
│  │    ├─ 记录语速样本 (remarkWindow)                 │    │
│  │    ├─ 重置 shortTimer (0.8s)                      │    │
│  │    ├─ 重置 longTimer (2.5s)                       │    │
│  │    │                                             │    │
│  │  shortTimer 到期 →                                │    │
│  │    ├─ 句末标点？ → ✅ 立即断句                    │    │
│  │    ├─ confidence > 0.7？ → ✅ 断句               │    │
│  │    └─ 否则 → 继续等待 longTimer                   │    │
│  │                                                  │    │
│  │  longTimer 到期 →                                 │    │
│  │    └─ ✅ 强制断句（兜底）                         │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ↓ 断句触发                                               │
│  pauseRecognition() → onResult(finalText)                │
└──────────────────────────────────────────────────────────┘
```

## 数据模型

无需新增持久化数据。运行时状态：

| 变量 | 类型 | 说明 |
|------|------|------|
| `shortTimer` | `ReturnType<typeof setTimeout> \| null` | 短超时定时器 (0.8s) |
| `longTimer` | `ReturnType<typeof setTimeout> \| null` | 长超时定时器 (2.5s) |
| `remarkWindow` | `Array<{time: number, chars: number}>` | 最近 5 次 interim 的 (时间戳, 字符数) 滑动窗口 |
| `SHORT_TIMEOUT_MS` | `800` | 常量：候选断句超时 |
| `LONG_TIMEOUT_MS` | `2500` | 常量：强制断句超时 |
| `CONFIDENCE_THRESHOLD` | `0.7` | 常量：高置信度阈值 |
| `MIN_TEXT_LENGTH` | `5` | 常量：最小可断句文本长度 |
| `SENTENCE_ENDINGS` | `Set` | `{。!?！？…}` 句末标点集合 |

## 接口定义

### 内部接口（不变更）

| 接口 | 签名 | 行为变化 |
|------|------|:--------:|
| `startListening()` | `(options) => Promise<boolean>` | 内部新增双定时器初始化 |
| `stopListening()` | `() => void` | 新增 shortTimer/longTimer 清理 |
| `pauseRecognition()` | `() => SpeechResult \| null` | **不变** |
| `resumeListening()` | `() => Promise<boolean>` | **不变** |
| `forceStop()` | `() => SpeechResult \| null` | **不变** |

### 新增内部函数

| 函数 | 签名 | 职责 |
|------|------|------|
| `calculateSpeechRate()` | `() => number` | 基于 remarkWindow 计算语速 (chars/s) |
| `hasSentenceEnding()` | `(text: string) => boolean` | 检查文本是否以句末标点结尾 |
| `shouldPauseEarly()` | `() => boolean` | 短超时决策：置信度 + 标点检查 |
| `clearTimers()` | `() => void` | 统一清理 shortTimer + longTimer |

## 核心逻辑伪代码

```typescript
// 在 rec.onresult 回调中，替代原有的 pauseTimer 逻辑

// 1. 语速跟踪
remarkWindow.push({ time: Date.now(), chars: interimText.length })
if (remarkWindow.length > 5) remarkWindow.shift()

// 2. 双定时器管理
clearTimers()

if (currentText.value.trim().length >= MIN_TEXT_LENGTH) {
  shortTimer = setTimeout(() => {
    if (shouldPauseEarly()) {
      triggerPause()
    }
  }, SHORT_TIMEOUT_MS)

  longTimer = setTimeout(() => {
    triggerPause()  // 强制断句
  }, LONG_TIMEOUT_MS)
}

function shouldPauseEarly(): boolean {
  const text = currentText.value.trim()
  // 句末标点 → 立即断
  if (hasSentenceEnding(text)) return true
  // 高置信度 + 较长文本 → 候选断
  if (lastConfidence > CONFIDENCE_THRESHOLD && text.length > 10) return true
  return false
}

function triggerPause() {
  const result = pauseRecognition()
  if (result) options.onResult?.(result)
}
```

## 门控状态

- [x] `architecture_documented`
- [x] `data_model_designed`
- [x] `interface_defined`
