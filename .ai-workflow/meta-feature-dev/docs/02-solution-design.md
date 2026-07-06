# 方案设计文档

## 项目信息
- 项目名称: interview-tiger
- 需求来源: [模块5-对话体验优化需求文档.md](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/.ai-workflow/meta-agent-collaboration/docs/模块5-对话体验优化需求文档.md)
- 创建时间: 2026-07-06
- 状态: 进行中

---

## R1: 滚动体验优化

### 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 方案A: 独立滚动容器 | 简单直接，用户体验好 | 内容过长时仍需滚动 | ⭐⭐⭐ |
| 方案B: 折叠展开 | 节省空间，一目了然 | 需要额外交互 | ⭐⭐⭐⭐ |
| 方案C: 两者结合 | 最优体验 | 实现稍复杂 | ⭐⭐⭐⭐⭐ |

### 推荐方案：方案C（独立滚动 + 折叠展开）

**设计思路**：
1. AI气泡内容超过200px高度时，自动启用独立滚动
2. 添加折叠/展开按钮，用户可手动控制显示高度
3. 默认展开前3行内容，点击展开显示全部

**技术实现**：
```css
.dialogue-bubble-ai-content {
  max-height: 200px;
  overflow-y: auto;
  transition: max-height 0.3s ease;
}
.dialogue-bubble-ai-content.expanded {
  max-height: none;
}
```

**修改文件**：
- `frontend/src/components/DialogueItem.vue` — 添加折叠按钮和滚动容器
- `frontend/src/assets/main.css` — 添加滚动样式和动画

---

## R2: UI结构化展示

### 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 方案A: 标题+内容分区 | 清晰直观，符合用户预期 | 需要修改模板结构 | ⭐⭐⭐⭐⭐ |
| 方案B: 卡片式布局 | 视觉层次分明 | 改动较大 | ⭐⭐⭐⭐ |
| 方案C: Markdown渲染 | 支持丰富格式 | 需要引入Markdown库 | ⭐⭐⭐ |

### 推荐方案：方案A（标题+内容分区）

**设计思路**：
1. 在AI气泡内区分