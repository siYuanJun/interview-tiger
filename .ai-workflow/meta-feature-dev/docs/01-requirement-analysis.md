# 需求分析文档

## 项目信息
- 项目名称: interview-tiger
- 需求描述: 修复语音识别延迟（添加手动结束按钮）+ UI整体翻新
- 创建时间: 2026-07-02
- 状态: 已完成

---

## R1: 语音识别延迟问题

### 问题描述
Web Speech API 的 `isFinal` 标志等待时间过长（1-3秒），导致用户体验不佳。

### 需求
添加手动结束按钮，允许用户在说完话后立即提交当前识别文本，无需等待 API 自动结束。

### 涉及模块
- `frontend/src/composables/useSpeech.ts`
- `frontend/src/components/InterviewPage.vue`

---

## R2: UI整体翻新

### 设计风格
- **风格**: Glassmorphism（毛玻璃效果）
- **主色调**: Navy（#1E3A5F）
- **字体**: Poppins + Open Sans

### 设计系统
- **Pattern**: Hero + Features + CTA
- **Colors**: Navy + Green
- **Elements**: 毛玻璃卡片、渐变背景、发光效果

### 涉及模块
- `frontend/src/assets/main.css`
- `frontend/src/App.vue`
- `frontend/src/components/InterviewPage.vue`
- `frontend/src/components/DialogueItem.vue`

---

## 约束条件
- 保持现有功能不变
- 兼容现有浏览器环境
- 不引入额外依赖