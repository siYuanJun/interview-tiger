# UI 设计系统全局样式规范计划

## 🎨 设计系统定位

### 产品定性：AI 面试助手工具
- **产品类型**：工具类 (AI Assistant Tool)
- **目标用户**：求职者、面试者
- **使用场景**：面试准备、实时面试辅助
- **风格关键词**：专业、科技感、深色主题、玻璃拟态

### 设计灵感来源：SVG Logo 主题
基于已设计的 `docs/hero.svg` 的视觉风格：
- **主色调**：蓝紫粉渐变 (`#60a5fa → #c084fc → #f472b6`)
- **Logo 色**：金色 (`#fbbf24`)
- **背景色**：深紫色 (`#0F0F23`)
- **效果**：发光、渐变、玻璃拟态

---

## 📐 设计系统规范

### 1. 色彩系统

#### 主色调（SVG Logo 主题）

| 角色 | 颜色 | CSS 变量 | 用途 |
|------|------|----------|------|
| **背景** | `#0F0F23` | `--color-background` | 页面主背景 |
| **前景** | `#E2E8F0` | `--color-foreground` | 主要文字 |
| **主色** | `#7C3AED` | `--color-primary` | 主按钮、高亮 |
| **主色浅** | `#818CF8` | `--color-primary-light` | 悬停效果 |
| **次要色** | `#A78BFA` | `--color-secondary` | 辅助元素 |
| **强调色** | `#F43F5E` | `--color-accent` | 重要操作、警告 |
| **Logo 金** | `#FBBF24` | `--color-gold` | Logo、品牌元素 |
| **卡片背景** | `rgba(30, 27, 75, 0.6)` | `--color-card-bg` | 玻璃拟态卡片 |
| **边框** | `rgba(123, 58, 237, 0.3)` | `--color-border` | 边框、分割线 |
| **禁用** | `#475569` | `--color-disabled` | 禁用状态 |
| **成功** | `#10B981` | `--color-success` | 成功状态 |
| **警告** | `#F59E0B` | `--color-warning` | 警告状态 |

#### 渐变系统

| 名称 | 渐变定义 | 用途 |
|------|----------|------|
| **主渐变** | `linear-gradient(90deg, #60a5fa, #c084fc, #f472b6)` | 按钮、标题、装饰 |
| **Logo 渐变** | `linear-gradient(135deg, #fbbf24, #f59e0b)` | Logo、品牌元素 |
| **卡片渐变** | `linear-gradient(135deg, rgba(123,58,237,0.1), rgba(192,132,252,0.1))` | 卡片背景 |

### 2. 字体系统

| 层级 | 字体大小 | 字重 | 行高 | 用途 |
|------|----------|------|------|------|
| H1 | 56px | 700 | 1.2 | 主标题 |
| H2 | 36px | 600 | 1.3 | 副标题 |
| H3 | 24px | 600 | 1.4 | 卡片标题 |
| H4 | 18px | 500 | 1.5 | 小标题 |
| Body | 16px | 400 | 1.6 | 正文 |
| Small | 14px | 400 | 1.5 | 辅助文字 |
| Tiny | 12px | 400 | 1.4 | 提示文字 |

### 3. 间距系统（8px 栅格）

| 名称 | 值 | 用途 |
|------|-----|------|
| xs | 4px | 内边距、图标间距 |
| sm | 8px | 小间距、元素间距 |
| md | 16px | 中等间距、卡片间距 |
| lg | 24px | 大间距、区块间距 |
| xl | 32px | 超大间距、页面间距 |
| 2xl | 48px | 页面头部、底部间距 |

### 4. 圆角系统

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | 8px | 按钮、输入框 |
| md | 12px | 卡片、模态框 |
| lg | 16px | 大卡片、容器 |
| xl | 24px | Logo、大按钮 |

### 5. 阴影系统

| 名称 | 值 | 用途 |
|------|-----|------|
| sm | `0 2px 8px rgba(0,0,0,0.3)` | 小元素 |
| md | `0 4px 16px rgba(123,58,237,0.2)` | 卡片 |
| lg | `0 8px 32px rgba(123,58,237,0.3)` | 模态框 |
| glow | `0 0 20px rgba(123,58,237,0.5), 0 0 40px rgba(192,132,252,0.3)` | Logo、按钮 |

---

## 🧩 组件规范

### 1. 按钮组件

| 类型 | 样式 | 状态 |
|------|------|------|
| **主按钮** | 渐变背景 + 发光效果 | 默认/悬停/点击/禁用 |
| **次按钮** | 透明背景 + 渐变边框 | 默认/悬停/点击/禁用 |
| **文字按钮** | 纯文字 | 默认/悬停/点击 |

### 2. 卡片组件（玻璃拟态）

```css
.glass-card {
  background: rgba(30, 27, 75, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(123, 58, 237, 0.3);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.glass-card:hover {
  border-color: rgba(192, 132, 252, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(123, 58, 237, 0.3);
}
```

### 3. 输入框组件

```css
.input-field {
  background: rgba(30, 27, 75, 0.8);
  border: 1px solid rgba(123, 58, 237, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  color: #E2E8F0;
  transition: all 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #818CF8;
  box-shadow: 0 0 0 3px rgba(123, 58, 237, 0.2);
}
```

---

## 📁 文件修改清单

| 文件 | 修改内容 |
|------|----------|
| `frontend/tailwind.config.js` | 更新颜色配置、字体、动画、间距 |
| `frontend/src/assets/main.css` | 添加全局样式、渐变、玻璃拟态 |
| `frontend/src/components/HomePage.vue` | 使用新样式重构首页 |
| `frontend/src/components/ConfigModal.vue` | 更新配置弹窗样式 |
| `frontend/src/components/InterviewPage.vue` | 更新面试页面样式 |
| `frontend/src/components/TigerLogo.vue` | 新建 Logo 组件 |

---

## 📝 实现步骤

### 步骤 1：更新 Tailwind 配置
- 添加自定义颜色（SVG 主题色）
- 添加渐变配置
- 添加动画配置
- 添加字体配置

### 步骤 2：创建全局样式
- 玻璃拟态卡片样式
- 渐变文字样式
- 按钮发光效果
- 滚动条样式
- 基础重置样式

### 步骤 3：创建 TigerLogo 组件
- 使用 SVG Logo
- 添加金色渐变和发光效果
- 添加浮动动画

### 步骤 4：重构首页
- 使用新的 Logo 组件
- 玻璃拟态卡片布局
- 渐变按钮样式
- 多层背景装饰

### 步骤 5：更新其他组件
- ConfigModal：玻璃拟态弹窗
- InterviewPage：统一风格

### 步骤 6：测试验证
- 响应式布局测试
- 动画性能测试
- 颜色对比度验证

---

## ✅ 预期效果

- **全局风格统一**：所有页面使用一致的配色和组件风格
- **SVG 主题延续**：颜色和效果与 hero.svg 保持一致
- **玻璃拟态效果**：卡片和弹窗具有现代感的磨砂玻璃效果
- **流畅动效**：悬停、过渡动画流畅自然
- **专业感提升**：整体视觉效果更加高级和专业