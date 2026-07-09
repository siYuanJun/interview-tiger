# Stage 1: 需求澄清 — M1 断句端点检测优化

> 生成时间：2026-07-09  
> 机械臂产出：`find_similar.json`（build_index 脚本 bug 跳过，已用代码探索替代）

---

## 1. 需求范围定义

| 要素 | 内容 |
|------|------|
| **核心目标** | 将 `useSpeech.ts` 中固定 1.5 秒超时的断句机制，替换为自适应策略 |
| **触发场景** | 面试双向对话中，系统需要准确判断"用户说完一句话/一个语义段落"，触发 LLM 回答 |
| **期望结果** | 慢速说话不被过早切断，快速说话不会延迟断句，断句时机准确率显著提升 |

## 2. 约束条件

| 类型 | 约束 | 来源 |
|------|------|------|
| 技术约束 | 必须基于 Web Speech API，不引入新 ASR 引擎 | R2 |
| 成本约束 | 免费方案，不依赖付费 API/SaaS | R5 |
| 性能约束 | 断句延迟 ≤ 1 秒（用户说完到触发 LLM 的时间窗） | 推导 |
| 兼容约束 | 不破坏现有 `pauseRecognition()` / `resumeListening()` 接口 | 代码兼容性 |
| 场景约束 | 双向对话，需区分"短暂思考停顿"和"说话结束" | R4 |

## 3. 相似模块（机械臂产出）

| 文件 | 相似度 | 角色 |
|------|:-----:|------|
| `frontend/src/composables/useSpeech.ts` | 41.2 | **核心改动目标** — 断句逻辑所在 |
| `frontend/env.d.ts` | 36.7 | 类型声明，需关注 SpeechRecognition API 类型 |
| `frontend/src/components/InterviewPage.vue` | 30.7 | 集成调度点，`handleSpeechResult()` 处理断句结果 |
| `backend/config.py` | 24.2 | 可增加断句相关配置项（如超时范围） |

## 4. 现状分析

### 4.1 当前断句流程

```
SpeechRecognition.onresult
  ├─ interimText → 重置 1.5s 超时定时器
  ├─ 1.5s 无新 interim → pauseRecognition() → stop+提交
  └─ finalChunk → 累积到 finalText，不触发断句
```

### 4.2 已知缺陷

| 缺陷 | 影响 |
|------|------|
| 固定 1.5s 超时 | 慢速者过早切断，快速者延迟 |
| `pauseRecognition()` 调用 `rec.stop()` | 完全停止识别实例，需 `resumeListening()` 重建，有启动开销 |
| `confidence` 未使用 | 低置信度 interim 结果与高置信度结果同等对待 |
| 无语义完整性检查 | 不会判断句子是否完整（是否有句末标点） |

## 5. 门控检查

| 门控条件 | 状态 | 证据 |
|----------|:----:|------|
| `scope_defined` | ✅ | 核心目标/触发场景/期望结果三要素完整 |
| `constraints_listed` | ✅ | 5 类约束（技术/成本/性能/兼容/场景） |
| `similar_modules_found` | ✅ | `find_similar.py` 产出 4 个相关模块 |

**🟢 Stage 1 完成，可推进至 Stage 2。**
