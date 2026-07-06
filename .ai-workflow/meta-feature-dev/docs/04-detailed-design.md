# 详细设计文档

## 项目信息
- 项目名称: interview-tiger
- 需求描述: 修复语音识别延迟（添加手动结束按钮）+ UI整体翻新
- 创建时间: 2026-07-02
- 状态: 已完成

---

## R1: 语音识别延迟修复详细设计

### 接口定义

#### useSpeech.ts

**新增方法: forceStop**

```typescript
/**
 * 强制停止语音识别，立即提交当前识别结果
 */
function forceStop(): void
```

**调用流程:**
1. 调用 `recognition.stop()` 停止识别
2. 将 `finalTranscript` 和 `interimTranscript` 合并
3. 触发 `onResult` 回调，传入合并后的文本
4. 重置状态（清空临时文本，设置 `isListening = false`）

**返回值:** void

#### InterviewPage.vue

**新增按钮组件:**

| 属性 | 类型 | 值 |
|------|------|-----|
| v-if | boolean | `isListening` |
| @click | function | `forceStop()` |
| 文案 | string | "完成" |
| 样式 | class | "finish-btn" |

### 数据结构

```typescript
interface SpeechState {
  isListening: boolean;
  finalTranscript: string;
  interimTranscript: string;
}
```

### 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 未开始识别时调用 forceStop | 静默忽略 |
| 识别停止失败 | 记录日志，不影响流程 |

---

## R2: UI整体翻新详细设计

### CSS 变量定义

```css
:root {
  /* 主色调 */
  --color-navy: #1E3A5F;
  --color-navy-dark: #0F2744;
  --color-navy-light: #2E5A8A;
  
  /* 辅助色 */
  --color-green: #2ECC71;
  --color-green-light: #58D68D;
  
  /* 玻璃效果 */
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-blur: 10px;
  
  /* 字体 */
  --font-family-title: 'Poppins', sans-serif;
  --font-family-body: 'Open Sans', sans-serif;
}
```

### 组件样式规范

#### 玻璃卡片基础样式

```css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}
```

#### 按钮样式

```css
.btn-primary {
  background: linear-gradient(135deg, var(--color-green), var(--color-green-light));
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
}
```

### 布局结构

#### App.vue

```html
<div class="app-container">
  <div class="background-gradient"></div>
  <router-view class="content"></router-view>
</div>
```

#### InterviewPage.vue

```html
<div class="interview-page">
  <header class="header glass-card">...</header>
  <main class="main-content">
    <div class="dialogue-list">
      <DialogueItem v-for="item in dialogues" :key="item.id" :item="item" />
    </div>
  </main>
  <footer class="footer glass-card">
    <div class="input-area">...</div>
    <button v-if="isListening" @click="forceStop" class="finish-btn">完成</button>
  </footer>
</div>
```

#### DialogueItem.vue

```html
<div class="dialogue-item glass-card" :class="{ 'user': item.isUser, 'ai': !item.isUser }">
  <div class="avatar">...</div>
  <div class="content">
    <p class="text">{{ item.text }}</p>
    <span class="timestamp">{{ item.timestamp }}</span>
  </div>
</div>
```

### 动画效果

| 元素 | 动画类型 | 触发时机 |
|------|----------|----------|
| 卡片 | 淡入 + 上移 | 进入视图 |
| 按钮 | 悬停上浮 + 发光 | hover |
| 识别状态 | 脉冲 | 正在识别 |

---

## 文件改动清单

| 文件 | 改动类型 | 改动内容 |
|------|----------|----------|
| useSpeech.ts | 修改 | 新增 forceStop() 方法 |
| InterviewPage.vue | 修改 | 添加完成按钮，更新样式 |
| DialogueItem.vue | 修改 | 应用 Glassmorphism 样式 |
| main.css | 修改 | 添加主题变量和全局样式 |
| App.vue | 修改 | 更新布局结构 |