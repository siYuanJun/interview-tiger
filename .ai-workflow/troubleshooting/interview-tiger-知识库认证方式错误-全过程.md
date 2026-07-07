# Interview Tiger 知识库认证方式错误问题排查全过程

---

## 1. 文档信息

| 项目 | 内容 |
|---|---|
| **项目名称** | Interview Tiger（面试虎） |
| **问题类型** | API 认证错误 / 知识库无法生效 |
| **排查时间** | 2026-07-06 ~ 2026-07-07 |
| **解决状态** | ✅ 已解决 |
| **文档目的** | 复盘沉淀，防止同类问题再次发生 |
| **问题简述** | 知识库检索接口一直返回 HTTP 403 错误，原因是使用了错误的认证方式（SignerV4 签名），应该使用 Bearer Token |

---

## 2. 问题背景

### 2.1 初始任务

用户反馈知识库功能未生效，当询问"你叫什么？"时，LLM 回答"我叫张三"而不是知识库中的"刘朝相"。

### 2.2 遇到的问题

- 知识库检索接口返回 HTTP 403 Forbidden
- 错误信息：`check sign error, please check your ak, sk and tenant id`
- 知识库列表接口同样返回 403

### 2.3 影响范围

- 面试虎项目的 RAG 功能完全失效
- 用户无法获得基于知识库的个性化回答

---

## 3. 问题现象（详细）

### 3.1 错误日志

```
[13:16:12] ERROR [interview-tiger] list_knowledge_bases 调用失败: Exception
[13:16:12] ERROR [interview-tiger] === API ERROR: list_knowledge_bases ===
Error Type: Exception
Error Message: HTTP 403: {"code":1000001,"message":"check sign error, please check your ak, sk and tenant id","request_id":"..."}
```

### 3.2 测试结果

```bash
$ python test_kb.py "你叫什么？"
...
【测试1: 知识库检索】
原始响应: {"code":1000001,"message":"check sign error, please check your ak, sk and tenant id"}
❌ HTTP错误: 403
...
【测试2: 大模型调用（含知识库）】
知识库上下文: 无
大模型回答: 我叫[你的姓名]。
❌ 回答未包含'刘朝相'，知识库可能未生效
```

### 3.3 curl 测试结果

使用 Bearer Token 方式：
```bash
$ curl -i -X POST \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer AKLTMDI1NzhhYzU3MGEwNDI0ODg0ODc5NjJiMjI2MTE5Zjg:T1dHT1puR0ZqWmpabU5tWVRZalpqTmpaaFpUQXlOR0ppTURSaE56UmxPR0pqTnpZeVltVQ==" \
  'https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge' \
  -d '{"name":"siyuan_jianli","query":"test","limit":2}'

HTTP/1.1 400 Bad Request
{"code":1000001,"message":"invalid api key"}
```

---

## 4. 问题分析过程（核心）

### 4.1 第一阶段：初步判断

| 假设 | 推理 | 尝试方案 | 结果 | 反思 |
|---|---|---|---|---|
| **假设1：签名代码错误** | 错误信息提示签名失败，可能是 SignerV4 实现有误 | 检查签名代码，添加 Host header，修正协议为 https | ❌ 仍返回 403 | SignerV4 签名本身没问题，问题可能在认证方式 |
| **假设2：AK/SK 格式错误** | SK 可能需要 Base64 解码 | 添加 double Base64 解码逻辑 | ❌ 仍返回 403 | 解码不是问题根源 |
| **假设3：服务名错误** | 文档中同时出现 "air" 和 "vikingdb" | 分别测试两种服务名 | ❌ 均返回 403 | 服务名不是问题 |
| **假设4：缺少账号 ID** | 错误信息提到 tenant id | 添加 V-Account-Id header | ❌ 仍返回 403 | 不是必需字段 |

### 4.2 第二阶段：深入分析

**关键转折点**：用户提供了官方 curl 示例

```bash
curl -i -X POST \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {VIKING_API_KEY}' \  # 注意：Bearer Token，不是 SignerV4！
  'https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge'
```

**深入调查步骤**：

1. **对比认证方式**：
   - 原代码使用：SignerV4 签名（AK:SK 格式）
   - 官方文档使用：Bearer Token（VIKING_API_KEY）

2. **验证新 API Key**：
   ```bash
   $ curl -i -X POST \
     -H 'Content-Type: application/json' \
     -H "Authorization: Bearer YOUR_VIKING_API_KEY" \
     'https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge' \
     -d '{"resource_id":"YOUR_KNOWLEDGEBASE_ID","project":"default","query":"你叫什么","limit":2}'

   HTTP/1.1 200 OK
   {"code":0,"message":"success","data":{"collection_name":"siyuan_jianli","count":2,"result_list":[...]}}
   ✅ 成功！
   ```

3. **根本原因解释**：
   - 火山引擎知识库 API 使用 **Bearer Token 认证**，不是 SignerV4 签名
   - `.env` 中配置的 `KB_API_KEY=AKLTxxx:SKxxx` 是用于其他 API 的格式
   - 需要从知识库控制台获取专门的 VIKING_API_KEY（纯字母数字格式）

---

## 5. 解决方案

### 5.1 最终方案

1. **获取正确的 API Key**：从火山引擎控制台 → 向量数据库 VikingDB → 知识库 → 用户管理 → API Key
2. **修改认证方式**：将 SignerV4 签名改为 Bearer Token
3. **修复知识库 ID**：使用 `resource_id` 参数（`kb-xxx` 格式）而非 `name`

### 5.2 代码修改

**文件**：[knowledge.py](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/app/services/knowledge.py)

```diff
- # 火山引擎知识库检索服务
- import json
- import requests
- from volcengine.auth.SignerV4 import SignerV4
- from volcengine.base.Request import Request
- from volcengine.Credentials import Credentials

+ # 火山引擎知识库检索服务
+ import json
+ import requests

- KB_API_URL = "https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge"
- KB_SERVICE = "air"
- KB_REGION = "cn-north-1"


- def _decode_base64_if_needed(sk):
-     try:
-         import base64
-         decoded = base64.b64decode(sk).decode('utf-8')
-         return decoded
-     except:
-         return sk


- def _decode_base64_double(sk):
-     try:
-         import base64
-         decoded = base64.b64decode(sk).decode('utf-8')
-         return base64.b64decode(decoded).decode('utf-8')
-     except:
-         return sk


- def _sign_request(method, path, ak, sk, data=None):
-     r = Request()
-     r.set_shema("https")
-     r.set_method(method)
-     r.set_connection_timeout(10)
-     r.set_socket_timeout(10)
-     
-     mheaders = {
-         "Accept": "application/json",
-         "Content-Type": "application/json",
-         "Host": "api-knowledgebase.mlp.cn-beijing.volces.com"
-     }
-     r.set_headers(mheaders)
-     r.set_host("api-knowledgebase.mlp.cn-beijing.volces.com")
-     r.set_path(path)
-     
-     if data is not None:
-         r.set_body(json.dumps(data))
-     
-     credentials = Credentials(ak, sk, KB_SERVICE, KB_REGION)
-     SignerV4.sign(r, credentials)
-     
-     return r.headers, r.body


- def search_knowledge(query: str, kb_id: str, kb_api_key: str):
-     if ':' in kb_api_key:
-         ak, sk = kb_api_key.split(':', 1)
-         sk = _decode_base64_double(sk)
-     else:
-         ak = kb_api_key
-         sk = ""
-     
-     path = "/api/knowledge/collection/search_knowledge"
-     
-     payload = {
-         'knowledgebase_id': kb_id,
-         'name': kb_id,
-         'project': 'default',
-         'query': query,
-         'limit': 3,
-         'post_processing': {
-             'rerank_switch': True,
-             'retrieve_count': 25
-         }
-     }
-     
-     headers, body = _sign_request('POST', path, ak, sk, payload)
-     
-     try:
-         response = requests.post(KB_API_URL, headers=headers, data=body, timeout=30)
+ def search_knowledge(query: str, kb_id: str, kb_api_key: str, project: str = "default", limit: int = 3, rerank: bool = True, retrieve_count: int = 25):
+     payload = {
+         'resource_id': kb_id,
+         'project': project,
+         'query': query,
+         'limit': limit,
+         'post_processing': {
+             'rerank_switch': rerank,
+             'retrieve_count': retrieve_count
+         }
+     }
+ 
+     headers = {
+         "Content-Type": "application/json",
+         "Authorization": f"Bearer {kb_api_key}"
+     }
+ 
+     try:
+         response = requests.post(KB_API_URL, headers=headers, json=payload, timeout=30)
```

### 5.3 配置调整

**文件**：[.env](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/.env)

```diff
- KB_API_KEY=AKLTMDI1NzhhYzU3MGEwNDI0ODg0ODc5NjJiMjI2MTE5Zjg:T1dHT1puR0ZqWmpabU5tWVRZalpqTmpaaFpUQXlOR0ppTURSaE56UmxPR0pqTnpZeVltVQ==
- KB_ID=siyuan_jianli
+ KB_API_KEY=YOUR_VIKING_API_KEY
+ KB_ID=YOUR_KNOWLEDGEBASE_ID
```

### 5.4 验证修复

```bash
$ python test_kb.py "你叫什么？"
...
【测试1: 知识库检索】
原始响应: {"code":0,"message":"success","data":{"collection_name":"siyuan_jianli","count":3,"result_list":[...]}}
过滤后知识内容:
✓ 命中 4052 字
内容: <KBDocName>01-自我介绍与核心必答题.md</KBDocName>...
...
【测试2: 大模型调用（含知识库）】
知识库上下文: 有
Prompt长度: 4370 字
大模型回答: 我叫刘朝相。
✓ 回答包含'刘朝相'，知识库生效！
```

---

## 6. 问题根因总结

### 6.1 根本原因表格

| 问题 | 根因 | 影响 |
|---|---|---|
| 认证方式错误 | 使用了 SignerV4 签名，应该使用 Bearer Token | 所有知识库请求返回 403 |
| API Key 格式错误 | 使用了 AK:SK 格式，应该使用 VIKING_API_KEY | Bearer Token 验证失败 |
| 知识库 ID 参数错误 | 使用了 `name` 参数，应该使用 `resource_id` | 可能无法正确定位知识库 |

### 6.2 为什么会发生

- 火山引擎官方文档中同时存在多种 API，认证方式各不相同
- 代码参考了错误的文档示例（SignerV4 签名示例）
- `.env` 文件中的注释和默认值未明确区分不同 API 的认证方式

### 6.3 为什么其他方案不行

| 方案 | 原因 |
|---|---|
| SignerV4 签名 | 知识库 API 不支持此认证方式，只支持 Bearer Token |
| 添加 V-Account-Id | 不是必需字段，添加后仍无法通过认证 |
| Base64 解码 SK | AK:SK 格式本身就是错误的，解码无法解决问题 |

---

## 7. 经验教训

### 7.1 最佳实践

1. **仔细阅读官方文档**：确认 API 的认证方式和参数格式
2. **先使用 curl 验证**：在编写代码前，先用 curl 测试 API 是否可用
3. **对比官方示例**：严格按照官方示例的认证方式和参数格式实现
4. **配置文件添加明确注释**：说明每个配置项的来源和格式要求

### 7.2 常见陷阱

1. **混淆不同 API 的认证方式**：火山引擎不同产品的 API 认证方式可能完全不同
2. **假设 AK:SK 是通用的**：AK:SK 只适用于部分 API，不是所有 API 都支持
3. **忽视错误信息中的关键词**：错误信息中的 "tenant id" 误导了排查方向，实际问题是认证方式
4. **盲目复制网上代码**：网上代码可能基于旧版 API，需要验证是否适用于当前版本

### 7.3 问题排查方法论

1. **从错误信息入手**：分析错误码和错误信息，不要忽略任何细节
2. **对比官方示例**：将代码与官方示例逐行对比
3. **简化测试**：使用 curl 等工具进行最小化测试，排除代码复杂性
4. **验证每个假设**：每个假设都要有可验证的结果，不要凭空猜测

---

## 8. 智能体技能提升要点

### 8.1 对 AI 助手的建议

遇到类似问题时，应按以下步骤思考：

1. **识别认证方式类型**：先判断 API 使用的是哪种认证方式（Bearer Token / SignerV4 / API Key）
2. **检查密钥格式**：确认密钥格式是否与认证方式匹配
3. **使用官方工具验证**：先用官方提供的工具（curl 示例、API Explorer）验证 API 是否可用
4. **对比代码与示例**：将代码实现与官方示例进行逐行对比

### 8.2 Mermaid 排查流程图

```mermaid
graph TD
    A[知识库请求失败] --> B{检查错误码}
    B -->|403| C[认证问题]
    B -->|400| D[参数问题]
    C --> E{认证方式}
    E -->|SignerV4| F[检查AK/SK]
    E -->|Bearer| G[检查API Key格式]
    F --> H[AK/SK是否正确]
    G --> I[API Key是否为VIKING格式]
    H -->|是| J[检查签名代码]
    H -->|否| K[获取正确AK/SK]
    I -->|是| L[检查参数]
    I -->|否| M[获取VIKING_API_KEY]
    J --> N[测试签名]
    L --> O[curl验证]
    K --> P[重新测试]
    M --> P
    N --> P
    O --> P
    P --> Q{是否成功}
    Q -->|是| R[✅ 解决]
    Q -->|否| S[继续分析]
    D --> T[检查参数格式]
    T --> U[curl验证参数]
    U --> P
```

### 8.3 关键命令速查

```bash
# 使用 curl 测试知识库检索（Bearer Token）
curl -i -X POST \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer YOUR_VIKING_API_KEY" \
  'https://api-knowledgebase.mlp.cn-beijing.volces.com/api/knowledge/collection/search_knowledge' \
  -d '{"resource_id":"kb-xxx","project":"default","query":"测试","limit":2}'

# 检查 Python 版本
python --version

# 查看环境变量
grep KB_API_KEY backend/.env
```

---

## 9. 相关配置文件修改清单

| 文件路径 | 修改位置 | 修改内容说明 |
|---|---|---|
| [.env](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/.env) | KB_API_KEY | 替换为 VIKING_API_KEY（纯字母数字） |
| [.env](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/.env) | KB_ID | 替换为知识库 ID（kb-xxx 格式） |
| [knowledge.py](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/app/services/knowledge.py) | 认证方式 | 从 SignerV4 签名改为 Bearer Token |
| [knowledge.py](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/app/services/knowledge.py) | 请求参数 | 使用 resource_id 替代 name 参数 |
| [knowledge.py](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/app/services/knowledge.py) | 过滤条件 | 调整分数过滤逻辑，避免误过滤 |
| [.env.example](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/.env.example) | 注释 | 添加获取位置说明，明确密钥格式 |
| [字节跳动接口调用指南.md](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/docs/字节跳动接口调用指南.md) | 知识库章节 | 更新认证方式说明和参数获取步骤 |

---

## 10. 参考资料

| 资料 | 链接 |
|---|---|
| 火山引擎知识库官方文档 | https://www.volcengine.com/docs/84313/1350012 |
| 火山引擎向量数据库 VikingDB | https://console.volcengine.com/vikingdb/knowledgebase/ |

---

## 11. 时间线记录

| 时间 | 事件 | 状态 |
|---|---|---|
| 2026-07-06 13:00 | 用户反馈知识库未生效 | 🔍 开始排查 |
| 2026-07-06 13:30 | 发现 HTTP 403 错误，错误信息为签名失败 | ❌ 未解决 |
| 2026-07-06 14:00 | 尝试修复 SignerV4 签名（添加 Host、修正协议、测试服务名） | ❌ 仍失败 |
| 2026-07-06 15:00 | 添加 double Base64 解码 | ❌ 仍失败 |
| 2026-07-06 16:00 | 创建 test_sign.py 单独测试签名 | ❌ 仍失败 |
| 2026-07-07 09:00 | 用户提供官方 curl 示例，发现使用 Bearer Token | 💡 关键发现 |
| 2026-07-07 10:00 | 获取 VIKING_API_KEY，使用 curl 测试成功 | ✅ 验证通过 |
| 2026-07-07 11:00 | 修改 knowledge.py 使用 Bearer Token | 🛠️ 修复代码 |
| 2026-07-07 12:00 | 修复过滤条件，测试完整流程 | ✅ 知识库生效 |
| 2026-07-07 13:00 | 更新文档和配置文件 | 📝 文档沉淀 |

---

## 12. 后续优化建议

### 短期（1周内）

1. ✅ 更新 [.env.example](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/backend/.env.example) 中的注释和默认值
2. ✅ 更新 [字节跳动接口调用指南.md](file:///Users/siyuan/Documents/www/ai-project/interview-tiger/docs/字节跳动接口调用指南.md)

### 中期（1个月内）

1. 添加 API Key 格式校验，启动时检测是否为正确格式
2. 添加知识库健康检查接口，定期验证知识库连接状态
3. 增加详细的错误日志，记录认证失败的原因和排查建议

### 长期（3个月内）

1. 实现多种认证方式的自动适配，根据配置自动选择认证方式
2. 添加 API Key 管理界面，支持在前端配置和验证知识库连接
3. 建立知识库连接测试机制，在配置变更时自动验证连接

---

## 13. 贡献者

| 角色 | 人员 | 贡献 |
|---|---|---|
| 问题发现者 | 用户 | 反馈知识库未生效问题 |
| 关键洞察提供者 | 用户 | 提供官方 curl 示例，指出正确的认证方式 |
| 问题分析者 | AI Agent | 分析错误原因，对比认证方式 |
| 解决方案提供者 | AI Agent | 修改代码，实现 Bearer Token 认证 |
| 文档编写者 | AI Agent | 编写排查全过程文档 |

---

> **文档版本**：v1.0  
> **最后更新**：2026-07-07  
> **维护建议**：定期更新参考资料链接，补充新的错误场景
