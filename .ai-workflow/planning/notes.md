# 开发笔记：实时语音显示模块

## 研究资料

- Web Speech API 文档：https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechRecognition
- SpeechRecognition.interimResults 属性：设为 true 可获取临时识别结果
- SpeechRecognition.continuous 属性：设为 true 持续监听

## 技术选型思路

当前使用 Web Speech API 的 isFinal 事件触发完成，导致用户需要等待识别完全结束才能看到文字。解决方案：
1. 设置 interimResults = true，实时获取临时结果并显示
2. 监听结果变化，维护一个计时器，2秒无变化则认为用户已说完
3. 提供手动"完成"按钮，用户可主动结束识别

## 上下文记录

### 2026-07-06 14:00
- 当前项目已完成基础语音识别功能，但存在3秒延迟问题
- 用户需求：边说边显示文字，停顿2秒自动完成，支持手动完成
- 需要修改的文件：useSpeech.ts、InterviewPage.vue

### 后续记录
- {思路/发现/决策}