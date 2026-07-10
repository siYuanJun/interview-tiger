# Stage 6: 实施记录 — M1 断句端点检测优化

## 实施概况

| 项目 | 详情 |
|------|------|
| 实施日期 | 2026-07-10 |
| 改动文件 | `frontend/src/composables/useSpeech.ts` |
| 新增行数 | ~55 行 |
| 修改行数 | ~10 行 |
| 删除行数 | 0 行（pauseTimer 保留，向后兼容） |
| 构建结果 | ✅ `vue-tsc` + `vite build` 零错误 |

## 逐步骤执行记录

### Step 1: 新增常量与运行时变量 ✅

新增 7 个常量和 4 个运行时变量：

| 变量 | 值 | 说明 |
|------|-----|------|
| `SHORT_TIMEOUT_MS` | 800 | 候选断句超时 |
| `LONG_TIMEOUT_MS` | 2500 | 强制断句超时 |
| `CONFIDENCE_THRESHOLD` | 0.7 | 高置信度阈值 |
| `MIN_TEXT_LENGTH` | 5 | 最小可断句文本长度 |
| `REMARK_WINDOW_SIZE` | 5 | 语速滑动窗口大小 |
| `SENTENCE_ENDINGS` | `{。！？…!?}` | 句末标点集合 |
| `shortTimer` / `longTimer` | — | 双定时器句柄 |
| `remarkWindow` | — | 语速跟踪窗口 |
| `lastConfidence` | — | 最后一次置信度 |

### Step 2: 实现 4 个辅助函数 ✅

- `calculateSpeechRate()` — 语速计算（chars/s），空窗口默认 5
- `hasSentenceEnding(text)` — 句末标点检测
- `shouldPauseEarly()` — 短超时决策（标点优先，置信度辅助）
- `clearTimers()` — 统一清理 shortTimer + longTimer

### Step 3: 重构 onresult 断句逻辑 ✅

将原固定 1.5s 单一定时器替换为双定时器策略：

```
每次 interim 事件 → 
  ├─ remarkWindow 记录语速样本
  ├─ lastConfidence 更新
  ├─ clearTimers() 重置
  ├─ 文本长度 ≥ 5 时启动双定时器：
  │   ├─ shortTimer (0.8s)  → shouldPauseEarly()? → 断句
  │   └─ longTimer (2.5s)   → 强制断句兜底
```

**与旧实现的兼容性**：`pauseTimer` 变量保留，`stopListening()` 中仍有清理逻辑。

### Step 4: stopListening 清理逻辑 ✅

新增 `clearTimers()` + `remarkWindow = []` + `lastConfidence = 0` 清理。

### Step 5: 构建验证 ✅

```bash
cd frontend && npm run build
# vue-tsc: 0 errors
# vite build: ✓ 1818 modules transformed in 5.91s
```

## 行为变化对比

| 场景 | 旧行为（1.5s 固定） | 新行为（双定时器自适应） |
|------|---------------------|-------------------------|
| 句末标点 "你好。" | 等 1.5s | 0.8s 内检测到标点立即断句 |
| 高置信度长句 | 等 1.5s | 0.8s 内置信度 > 0.7 优先断句 |
| 无标点低置信短句 | 等 1.5s | 2.5s 强制兜底 |
| 语速快用户 | 1.5s 可能切断未说完的话 | 2.5s 长超时给缓冲 |
| 语速慢用户 | 1.5s 断句太快 | 0.8s 先候选检查，有标点才断 |

## 风险评估

| 风险 | 状态 |
|------|------|
| 双定时器竞态 | ✅ `generation` 计数器保护，过期回调自动跳过 |
| 置信度不可用 | ✅ 默认 0，走长超时兜底路径 |
| API 兼容性 | ✅ `pauseRecognition` / `forceStop` 接口不变 |
| 浏览器兼容 | ✅ `confidence` 在 Chrome/Edge 可用，Safari 不支持 Web Speech API 无影响 |
