# 接口参数提取报告

## 接口信息

| 项目 | 内容 |
|------|------|
| HTTP 方法 | POST |
| URL 路径 | /api/question/stream |
| 来源文件 | backend/app/routes/question.py:113 |
| 返回类型 | SSE (Server-Sent Events) |
| 媒体类型 | text/event-stream |

## 参数提取表

| 参数名 | 类型 | 必填 | 默认值 | 来源 | 说明 |
|--------|------|------|--------|------|------|
| question | str | 是 | - | question.py:17 | 面试官问题文本，min_length=1, max_length=2000 |
| ark_api_key | str | 否 | "" | question.py:18 | 火山引擎API Key（留空则使用.env配置） |
| model_id | str | 否 | ARK_MODEL | question.py:19 | 模型ID |
| kb_id | str | 否 | "" | question.py:20 | 知识库ID（留空则使用.env配置） |
| kb_api_key | str | 否 | "" | question.py:21 | 知识库API Key（留空则使用.env配置） |
| kb_provider | str | 否 | "" | question.py:22 | 知识库提供者（volcengine/local） |
| stream | bool | 否 | True | question.py:23 | 是否流式输出 |

## 请求体示例

```json
{
    "question": "他也别想",
    "ark_api_key": "",
    "model_id": "deepseek-v4-flash-260425",
    "kb_id": "kb-ee95868bec0b4da8",
    "kb_api_key": "",
    "kb_provider": "volcengine",
    "stream": true
}
```

## SSE 响应格式

根据 question.py:142-159 的生成器逻辑：

| 类型 | 格式 | 说明 |
|------|------|------|
| status | `data: {"type": "status", "message": "..."}` | 状态消息（如"正在生成回答..."） |
| chunk | `data: {"type": "chunk", "content": "..."}` | 内容片段 |
| error | `data: {"type": "error", "message": "..."}` | 错误消息 |
| done | `data: [DONE]` | 结束标记 |

## 验证规则

1. **ark_api_key 必填校验**: question.py:119-120 - 若未配置会返回 400 错误
2. **question 长度校验**: question.py:17 - min_length=1, max_length=2000
3. **知识库降级逻辑**: question.py:135-137 - 无匹配结果时开启联网搜索