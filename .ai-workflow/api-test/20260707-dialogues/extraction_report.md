# 机械臂提取报告

## 接口信息

| 提取项 | 值 | 来源 |
|--------|-----|------|
| HTTP 方法 | GET | transcript.py:87 @router.get |
| URL 路径 | /api/dialogues | transcript.py:87 |
| 参数名 | session_id | transcript.py:88 |
| 参数类型 | Optional[str] | transcript.py:88 |
| 参数必填 | 否 | transcript.py:88 |
| 返回类型 | TranscriptResponse | transcript.py:87 |

## 路由注册

后端路由通过 `prefix="/api"` 注册，完整路径为 `/api/dialogues`（main.py:89）

## 返回字段

| 字段 | 类型 | 来源 |
|------|------|------|
| code | int | 统一响应格式 |
| message | string | 统一响应格式 |
| data.dialogues | list | transcript.py:112 |
| data.dialogues[].id | string | transcript.py:99 |
| data.dialogues[].question | string | transcript.py:100 |
| data.dialogues[].answer | string | transcript.py:101 |
| data.dialogues[].is_valid | bool | transcript.py:102 |
| data.dialogues[].rule | string | transcript.py:103 |
| data.dialogues[].created_at | string | transcript.py:104 |
| data.dialogues[].session_id | string | transcript.py:105 |
