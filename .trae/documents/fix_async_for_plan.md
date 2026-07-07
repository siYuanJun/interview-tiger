# 修复 'async for' 错误方案

## 问题描述

错误信息：`'async for' requires an object with __aiter__ method, got _asyncio.Future`

## 根因分析

在 `app/routes/question.py` 的流式生成接口中，代码试图用 `async for` 遍历 `loop.run_in_executor()` 的返回值：

```python
async for chunk in loop.run_in_executor(
    None,
    call_llm_stream,
    ...
):
```

问题在于：
1. `call_llm_stream` 是**同步生成器函数**（`def` + `yield`），返回 `Generator[str, None, None]`
2. `loop.run_in_executor()` 返回 `_asyncio.Future` 对象
3. `async for` 需要实现 `__aiter__` 方法的异步可迭代对象，而 `Future` 没有此方法

## 修复方案

### 方案一：使用 await 获取生成器后用普通 for 循环（推荐）

修改 `question.py` 中的 `generate()` 函数：

```python
async def generate():
    try:
        status_msg = "知识库+联网搜索中..." if use_web_search else "正在生成回答..."
        yield f"data: {json.dumps({'type': 'status', 'message': status_msg}, ensure_ascii=False)}\n\n"

        loop = asyncio.get_event_loop()
        # 使用 await 获取同步生成器
        generator = await loop.run_in_executor(
            None,
            call_llm_stream,
            messages,
            cfg["ark_api_key"],
            cfg["model_id"],
            0.7,
            1000,
            use_web_search
        )
        # 用普通 for 循环遍历生成器
        for chunk in generator:
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"流式生成异常: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
```

### 方案二：将 call_llm_stream 改为异步生成器

将 `app/services/llm.py` 中的 `call_llm_stream` 改为 `async def`，并使用 `async for` 遍历响应流。此方案改动较大，风险较高。

## 涉及文件

| 文件 | 修改内容 |
|------|----------|
| `app/routes/question.py` | 修改 `generate()` 函数，将 `async for` 改为 `await` + 普通 `for` |

## 风险评估

| 风险项 | 等级 | 说明 |
|--------|------|------|
| 修改简单 | 低 | 只需改动几行代码 |
| 不影响其他功能 | 低 | 只修改流式生成逻辑 |
| 测试验证 | 中 | 需要测试流式接口是否正常工作 |

## 验证方法

1. 启动后端服务
2. 调用 `/api/question/stream` 接口（带 `stream: true` 参数）
3. 验证是否能正常收到 SSE 流式响应
