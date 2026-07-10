# 开发笔记

---

## RAG 3.0 混合检索升级（2026-07-10）

### 技术选型思路

当前知识库检索使用纯向量检索（ChromaDB similarity_search），存在语义漂移、无法处理精确关键词匹配等问题。RAG 3.0 方案：
1. **P0 混合检索**：BM25（精确关键词） + Dense（语义理解） + RRF 融合排序，权重 BM25=0.3 / Dense=0.7
2. **P0 查询扩展**：构建面试领域同义词词典，生成最多 3 个查询变体
3. **P1 内容校验**：LLM 批量判断检索片段相关性，过滤噪音
4. **P2 多轮记忆**：会话级缓存，检测"还有呢""继续说"等追问复用上次结果

### 上下文记录

#### 2026-07-10 12:00
- 使用 meta-feature-dev 7 阶段工作流
- 路径 A：BM25+Dense 混合检索（非路径 B 的 full-text index 方案）
- 依赖：LangChain BM25Retriever + Chroma EnsembleRetriever

#### 2026-07-10 15:00
- Docker 测试坑：macOS `pip download` 下载的 wheels 与 Linux 容器不兼容
- 教训：永远不要在宿主机下载 wheels 给 Docker 用，架构不同

#### 2026-07-10 17:00
- pydantic 2.6.1 + Python 3.12 兼容性 Bug：langsmith 内部调用 `ForwardRef._evaluate()` 缺少参数
- 修复：升级 pydantic 到 2.13.4

#### 2026-07-10 17:50
- rank_bm25 缺失导致 BM25 回退，仅日志警告不影响功能
- 修复：`pip install rank_bm25==0.2.2`

#### 2026-07-10 18:00
- Docker 重建慢的根因：requirements.txt 新增 jieba 导致 pip 层缓存失效，PyTorch ~800MB 重下
- 最优方案：不重建，用 `docker exec pip install` 直装缺失包
- 长期方案：site-packages 全量快照（2.8G tar.gz）+ Dockerfile 条件解压

#### 2026-07-10 18:05
- api-test-harness 7/7 全部通过
- 四大模块日志确认激活：QueryRewriter / Hybrid BM25=0.3 / Validator 6→1 / Memory hit

#### 2026-07-10 20:00
- Dockerfile 优化：pip 全局清华源（`/root/.pip/pip.conf`），所有 `pip install` 自动走镜像
- Dockerfile 可选快照：`site-packages.tar.gz` 不存在时自动降级到 pip install

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

### 2026-07-06 14:30
- **实现方案**：在 useSpeech.ts 的 onresult 回调中，每次有 interim 结果时重置 pauseTimer，2秒后无更新则触发 forceStop
- **UI 实现**：InterviewPage.vue 添加 interimDialogue 临时对话对象，非 final 时实时渲染，final 后自动清除
- **关键修改**：移除 `handleSpeechResult` 中的 `if (!result.isFinal) return` 判断，改为实时更新临时对话

### 2026-07-06 14:45
- **测试结果**：API 测试全部通过（8/8），前端服务正常运行
- **完成状态**：TASK-022 实时语音显示模块已完成，进度从84%提升至92%