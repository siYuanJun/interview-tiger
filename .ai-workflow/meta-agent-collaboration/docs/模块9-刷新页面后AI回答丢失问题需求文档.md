# 模块9：刷新页面后AI回答丢失问题需求文档

## 一、问题背景

### 问题编号：BUG-9-001
**原文**：刷新面试页面后，大模型返回的数据没有显示，一直显示加载loading。但是重新说话就有了。

**业务解读**：用户在面试过程中刷新页面，已生成的AI回答丢失，UI显示loading动画，需要重新触发对话才能恢复。

---

## 二、需求质量门控

### 第一关：文本扫描
| 维度 | 结果 | 说明 |
|------|------|------|
| 可读性 | ✅ | 问题描述清晰：刷新→回答丢失→loading |
| 完整度 | ✅ | 含复现条件（刷新）和现象（loading卡死） |

→ 🟢 放行

### 第二关：上下文深评
| 维度 | 结果 | 说明 |
|------|------|------|
| 项目关联度 | ✅ | 直接关联 InterviewPage.vue + SSE 流式响应链路 |
| 可行性 | ✅ | 技术栈支持，对话状态管理已有基础 |

→ 🟢 放行

---

## 三、三层认知模型

### Layer 1：事实锚定层

| 编号 | 原文 | 
|------|------|
| F-001 | 刷新面试页面 |
| F-002 | 大模型返回来的数据没有显示 |
| F-003 | 一直是显示加载loading |
| F-004 | 重新说话它就有了 |

### Layer 2：业务解读层

| 编号 | 解读 |
|------|------|
| B-001 | 用户在 SSE 流式响应期间或之后刷新页面 |
| B-002 | 刷新后通过 `getDialogues(sessionId)` 从数据库恢复对话 |
| B-003 | 恢复的对话中 `answer` 字段为空字符串 |
| B-004 | DialogueItem 中 `v-if="item.answer"` 为 falsy，触发 `v-else` 显示 loading |
| B-005 | 重新说话触发新的 `submitTranscript` → SSE，新对话正常 |

### Layer 3：技术推导层（已验证）

| 编号 | 推导 | 验证 |
|------|------|------|
| T-001 | submitTranscript 创建 Dialogue 时 `answer=''` | ✅ [transcript.py:61](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/app/routes/transcript.py#L61) |
| T-002 | SSE onDone 时调用 updateDialogue 保存 answer | ✅ [InterviewPage.vue:158](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/frontend/src/components/InterviewPage.vue#L158) |
| T-003 | updateDialogue 是 fire-and-forget（未 await） | ✅ [InterviewPage.vue:158](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/frontend/src/components/InterviewPage.vue#L158) |
| T-004 | DialogueItem 用 `v-if="item.answer"` 判断是否显示 loading | ✅ [DialogueItem.vue:94](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/frontend/src/components/DialogueItem.vue#L94) |
| T-005 | 刷新时 getDialogues 返回数据库中已持久化的数据 | ✅ [transcript.py:87-114](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/app/routes/transcript.py#L87-L114) |

---

## 四、根因分析

```
用户说话 → submitTranscript → 后端创建 Dialogue(answer='')
  → 前端 push 到 dialogues (answer 为空, generating=true)
  → SSE stream 开始填充 answer
  → SSE done → updateDialogue 保存到数据库
                    ↑
              如果在 SSE 期间刷新页面：
              → fetch() 连接断开，onDone 从未触发
              → updateDialogue 从未调用
              → 数据库里 answer=''
              → getDialogues 返回 answer=''
              → v-if="item.answer" 为 falsy
              → 显示 loading 圆点（永远转圈）
```

**核心矛盾**：对话创建时 `answer=''`，刷新后无法区分"正在生成中"和"历史对话但答案为空"。

---

## 五、解决方案

### 修复方案：增加 `generating` 状态字段

| 场景 | `generating` | `answer` | UI 表现 |
|------|:--:|------|------|
| 新对话，SSE 生成中 | `true` | `""` | loading 动画 |
| SSE 完成 | `false` | 有内容 | MD 渲染 |
| 刷新后加载历史 | `undefined` | `""` | "回答未生成" |
| 刷新后加载历史 | `undefined` | 有内容 | MD 渲染 |

### 代码修改

1. **Dialogue 接口**：新增 `generating?: boolean`
2. **创建对话时**：`dialogue.generating = true`
3. **SSE onDone**：`dialogues.value[idx].generating = false`
4. **SSE onError**：`dialogues.value[idx].generating = false`
5. **DialogItem**：`v-else-if="generating"` 显示 loading，`v-else` 显示"回答未生成"

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| [InterviewPage.vue](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/frontend/src/components/InterviewPage.vue) | 接口 + creating + done/error |
| [DialogueItem.vue](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/frontend/src/components/DialogueItem.vue) | 新增 generating prop + 三态渲染 |

---

## 六、验收标准

1. 正常面试流程：AI回答正常显示
2. AI回答生成中：显示loading圆点动画
3. 刷新页面后：已有回答的对话正常显示，空回答的对话显示"回答未生成"
4. 刷新页面后新说话：新对话正常生成并显示

---

**文档版本**：v1.0  
**创建日期**：2026-07-08  
**问题类型**：Bug Fix  
**涉及组件**：InterviewPage.vue, DialogueItem.vue
