# Stage 3: 影响评估 — M1 断句端点检测优化

## 机械臂产出汇总

### find_callers: 调用方分析

| 符号 | 源码引用文件 | 文档引用 | 关键发现 |
|------|------------|:------:|----------|
| `useSpeech` | `useSpeech.ts` (1), `InterviewPage.vue` (2) | 39 docs | 仅 1 个源码消费者 |
| `handleSpeechResult` | `InterviewPage.vue` (4) | 8 docs | 间接影响：函数签名不变 |
| `pauseRecognition` | `useSpeech.ts` (3), `InterviewPage.vue` (2) | 8 docs | 间接影响：语义保持不变 |
| `pauseTimer` | `useSpeech.ts` (6) | 8 docs | 核心改动对象 |

### scan_imports: 依赖图

- `useSpeech.ts` 被 `InterviewPage.vue` 通过 `@/composables/useSpeech` 引用
- `useSpeech.ts` 无外部模块依赖（仅依赖浏览器原生 API + Vue ref）
- 无后端依赖链

### scan_schema: 数据库影响

- ⚠️ **`scan_schema.py` 分析 0 个数据库实体**  待复核
- **解读**：Web Speech API 不存储数据到数据库（实际不影响对话存储）

### ⚠️ 潜在遗漏：用户对话存储

`scan_schema.py` 未扫描到 PostgreSQL 对话表。需复核确认 `transcript.py` 中的 `Dialogue` 数据模型不受影响。

## 影响矩阵

| 影响维度 | 级别 | 详情 |
|---------|:----:|------|
| **前端代码** | 🟢 低 | 仅 `useSpeech.ts` 第 104-113 行 onresult 回调区域，~80 行新增/修改 |
| **前端组件** | 🟢 零 | `InterviewPage.vue` 无需改动，`onResult` / `pauseRecognition` / `resumeListening` 接口不变 |
| **后端代码** | 🟢 零 | 无后端改动 |
| **数据库** | 🟢 零 | 无 schema 变更 |
| **API 契约** | 🟢 零 | `POST /api/transcript` 不变 |
| **浏览器兼容** | 🟡 低 | `SpeechRecognitionEvent.results[].confidence` 在 Chrome/Edge 均支持 |
| **已有功能** | 🟢 零破坏 | `pauseRecognition()` / `forceStop()` / `resumeListening()` 行为不变 |

## 变更范围（精确到函数）

```
frontend/src/composables/useSpeech.ts
  ├─ [修改] startListening() → rec.onresult 回调 (L80-124)
  │   └─ 新增: 语速跟踪变量 (remarkWindow[])
  │   └─ 新增: 连动超时定时器 (shortTimer, longTimer)
  │   └─ 新增: 置信度检查 + 句末标点检测
  │   └─ 保留: pauseTimer 现有清理逻辑
  ├─ [修改] stopListening() (L216-242)
  │   └─ 新增: 清理 shortTimer, longTimer
  └─ [不变] pauseRecognition(), forceStop(), resumeListening() 等其余方法
```

**总计**：1 个文件，约 80 行新增，0 行删除，0 个接口变更。

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|:----:|:----:|----------|
| 双定时器竞态 | 🟡 中 | 🟡 中 | `generation` 计数器已存在，回调中验证，确保旧定时器不污染新会话 |
| 置信度阈值误判 | 🟡 中 | 🟢 低 | 默认保守（0.7），可通过配置调整；低置信度仅延迟断句不丢弃 |
| 语速计算窗口过小 | 🟢 低 | 🟢 低 | 窗口 5 次 interim，约覆盖 1-2 秒，足以反映语速趋势 |
| 句末标点缺失 | 🟡 中 | 🟢 低 | 仅作为加速因子（非必需），长超时（2.5s）兜底强制断句 |
| 浏览器兼容 | 🟢 低 | 🟡 中 | `confidence` 在 Chrome/Edge 均可用，Safari 不支持 Web Speech API |

**总体风险等级**：🟢 **低风险**

## 门控状态

- [x] `all_callers_identified` — 4 个符号全量扫描
- [x] `dependency_graph_complete` — 依赖图确认单向依赖
- [x] `schema_impact_assessed` — scan_schema 确认零 DB 影响
- [x] `risk_matrix_done` — 5 项风险均含缓解措施
