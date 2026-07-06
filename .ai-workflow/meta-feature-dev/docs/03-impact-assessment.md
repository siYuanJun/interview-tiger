# 影响评估文档

## 项目信息
- 项目名称: interview-tiger
- 需求描述: 修复语音识别延迟（添加手动结束按钮）+ UI整体翻新
- 创建时间: 2026-07-02
- 状态: 已完成

---

## R1: 语音识别延迟修复影响评估

### 影响范围

#### 调用者分析
| 调用者 | 文件路径 | 影响程度 |
|--------|----------|----------|
| InterviewPage.vue | frontend/src/components/InterviewPage.vue | 高 |
| useRecorder.ts | frontend/src/composables/useRecorder.ts | 低 |

#### 依赖关系
```
useSpeech.ts ← InterviewPage.vue
    ↓
Web Speech API
```

### 风险评估
| 风险项 | 风险等级 | 影响描述 | 缓解措施 |
|--------|----------|----------|----------|
| 强制停止导致文本截断 | 低 | 可能丢失部分未确认的识别结果 | 在停止前记录当前所有临时结果 |
| 按钮状态管理 | 低 | 按钮显示/隐藏状态可能不同步 | 使用响应式状态统一管理 |

### 改动清单
- `frontend/src/composables/useSpeech.ts`: 新增 `forceStop()` 方法
- `frontend/src/components/InterviewPage.vue`: 添加完成按钮组件

---

## R2: UI整体翻新影响评估

### 影响范围

#### 调用者分析
| 调用者 | 文件路径 | 影响程度 |
|--------|----------|----------|
| main.ts | frontend/src/main.ts | 高（引入样式） |
| App.vue | frontend/src/App.vue | 高 |
| InterviewPage.vue | frontend/src/components/InterviewPage.vue | 高 |
| DialogueItem.vue | frontend/src/components/DialogueItem.vue | 高 |

#### 依赖关系
```
main.css → App.vue → InterviewPage.vue → DialogueItem.vue
```

### 风险评估
| 风险项 | 风险等级 | 影响描述 | 缓解措施 |
|--------|----------|----------|----------|
| 样式冲突 | 中 | 可能覆盖现有样式导致组件异常 | 使用 CSS 变量和 scoped 样式 |
| 浏览器兼容性 | 中 | backdrop-filter 在旧浏览器不支持 | 添加降级样式 |
| 布局破坏 | 中 | 可能导致某些布局错位 | 逐步更新，逐一测试 |

### 改动清单
- `frontend/src/assets/main.css`: 添加 Glassmorphism 主题变量和全局样式
- `frontend/src/App.vue`: 更新布局结构和样式
- `frontend/src/components/InterviewPage.vue`: 更新组件样式
- `frontend/src/components/DialogueItem.vue`: 更新对话卡片样式

---

## 总体评估

| 指标 | 评级 |
|------|------|
| 代码改动量 | 中等 |
| 风险等级 | 中 |
| 测试覆盖要求 | 高 |
| 回滚难度 | 低 |

---

## 建议
1. R1 和 R2 可以并行开发
2. R2 建议按组件逐步更新，便于测试和回滚
3. 完成后进行完整的功能回归测试