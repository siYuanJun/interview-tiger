# 问题处理路由 - 面试核心API
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
import asyncio
import time

from config import ARK_MODEL, ARK_API_KEY, KB_ID, KB_API_KEY
from app.services.knowledge import get_relevant_knowledge
from app.services.llm import call_llm, call_llm_stream
from app.services.prompt import build_messages
from app.utils.logger import logger, log_api_error
router = APIRouter()


class QuestionRequest(BaseModel):
    """问题处理请求"""
    question: str = Field(..., min_length=1, max_length=2000, description="面试官问题文本")
    ark_api_key: str = Field(default="", description="火山引擎API Key（留空则使用.env配置）")
    model_id: str = Field(default=ARK_MODEL, description="模型ID")
    kb_id: str = Field(default="", description="知识库ID（留空则使用.env配置）")
    kb_api_key: str = Field(default="", description="知识库API Key（留空则使用.env配置，AK:SK格式）")
    stream: bool = Field(default=True, description="是否流式输出")


def resolve_config(req: QuestionRequest):
    """解析配置：前端传入优先，否则使用.env默认值"""
    return {
        "ark_api_key": req.ark_api_key or ARK_API_KEY,
        "model_id": req.model_id or ARK_MODEL,
        "kb_id": req.kb_id or KB_ID,
        "kb_api_key": req.kb_api_key or KB_API_KEY,
    }


class QuestionResponse(BaseModel):
    """问题处理响应"""
    code: int = 0
    message: str = "success"
    data: dict = {}


@router.post("/question")
async def process_question(req: QuestionRequest):
    """处理面试问题 - 非流式版本

    优化：知识库检索与大模型准备并行执行，减少延迟。
    知识库无结果时自动降级为联网搜索模式。
    """
    logger.info(f"处理面试问题: {req.question[:50]}...")

    cfg = resolve_config(req)

    if not cfg["ark_api_key"]:
        raise HTTPException(status_code=400, detail="ARK_API_KEY未配置，请在.env或请求中提供")

    knowledge_context = ""
    use_web_search = False

    async def fetch_knowledge():
        nonlocal knowledge_context
        if cfg["kb_id"] and cfg["kb_api_key"]:
            logger.info(f"检索知识库: {cfg['kb_id']}")
            knowledge_context = await asyncio.to_thread(
                get_relevant_knowledge,
                query=req.question,
                kb_id=cfg["kb_id"],
                kb_api_key=cfg["kb_api_key"]
            )
            if knowledge_context:
                logger.info(f"知识库命中: {len(knowledge_context)}字")

    await fetch_knowledge()

    if not knowledge_context:
        logger.info("知识库无匹配结果，开启联网搜索降级模式")
        use_web_search = True

    messages = build_messages(req.question, knowledge_context, use_web_search)

    answer = await asyncio.to_thread(
        call_llm,
        messages=messages,
        api_key=cfg["ark_api_key"],
        model=cfg["model_id"],
        temperature=0.7,
        max_tokens=1000,
        enable_search=use_web_search
    )

    if answer is None:
        log_api_error("process_question", Exception("大模型调用失败"), {"question": req.question[:50]})
        raise HTTPException(status_code=500, detail="大模型调用失败，请检查API Key配置")

    return {
        "code": 0,
        "message": "success",
        "data": {
            "answer": answer,
            "knowledge_used": bool(knowledge_context),
            "web_search_used": use_web_search,
            "source_chunks": []
        }
    }


@router.post("/question/stream")
async def process_question_stream(req: QuestionRequest):
    """处理面试问题 - 流式版本（SSE）

    优化：知识库检索与大模型准备并行执行，减少延迟。
    知识库无结果时自动降级为联网搜索模式。
    """
    logger.info(f"流式处理面试问题: {req.question[:50]}...")

    cfg = resolve_config(req)

    if not cfg["ark_api_key"]:
        raise HTTPException(status_code=400, detail="ARK_API_KEY未配置，请在.env或请求中提供")

    knowledge_context = ""
    use_web_search = False

    async def fetch_knowledge():
        nonlocal knowledge_context
        if cfg["kb_id"] and cfg["kb_api_key"]:
            knowledge_context = await asyncio.to_thread(
                get_relevant_knowledge,
                query=req.question,
                kb_id=cfg["kb_id"],
                kb_api_key=cfg["kb_api_key"]
            )

    await fetch_knowledge()

    if not knowledge_context:
        logger.info("知识库无匹配结果，开启联网搜索降级模式")
        use_web_search = True

    messages = build_messages(req.question, knowledge_context, use_web_search)

    async def generate():
        """SSE流式生成器"""
        try:
            status_msg = "知识库+联网搜索中..." if use_web_search else "正在生成回答..."
            yield f"data: {json.dumps({'type': 'status', 'message': status_msg}, ensure_ascii=False)}\n\n"

            loop = asyncio.get_event_loop()
            async for chunk in loop.run_in_executor(
                None,
                call_llm_stream,
                messages,
                cfg["ark_api_key"],
                cfg["model_id"],
                0.7,
                1000,
                use_web_search
            ):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"流式生成异常: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )