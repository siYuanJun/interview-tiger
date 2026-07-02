# 问题处理路由 - 面试核心API
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from config import ARK_MODEL
from app.services.knowledge import get_relevant_knowledge
from app.services.llm import call_llm, call_llm_stream
from app.services.prompt import build_messages

logger = logging.getLogger("interview-tiger")
router = APIRouter()


class QuestionRequest(BaseModel):
    """问题处理请求"""
    question: str = Field(..., min_length=1, max_length=2000, description="面试官问题文本")
    ark_api_key: str = Field(..., description="火山引擎API Key")
    model_id: str = Field(default=ARK_MODEL, description="模型ID")
    kb_id: str = Field(default="", description="知识库ID（可选）")
    kb_api_key: str = Field(default="", description="知识库API Key（可选，AK:SK格式）")
    stream: bool = Field(default=True, description="是否流式输出")


class QuestionResponse(BaseModel):
    """问题处理响应"""
    code: int = 0
    message: str = "success"
    data: dict = {}


@router.post("/question")
async def process_question(req: QuestionRequest):
    """处理面试问题 - 非流式版本

    完整流程：知识库检索 → Prompt拼接 → 大模型生成 → 返回回答
    """
    logger.info(f"处理面试问题: {req.question[:50]}...")

    # 第1步：知识库检索（如已配置）
    knowledge_context = ""
    if req.kb_id and req.kb_api_key:
        logger.info(f"检索知识库: {req.kb_id}")
        knowledge_context = get_relevant_knowledge(
            query=req.question,
            kb_id=req.kb_id,
            kb_api_key=req.kb_api_key
        )
        if knowledge_context:
            logger.info(f"知识库命中: {len(knowledge_context)}字")
        else:
            logger.info("知识库无匹配结果，降级为通用模式")

    # 第2步：构建Prompt
    messages = build_messages(req.question, knowledge_context)

    # 第3步：调用大模型
    answer = call_llm(
        messages=messages,
        api_key=req.ark_api_key,
        model=req.model_id,
        temperature=0.7,
        max_tokens=1000
    )

    if answer is None:
        raise HTTPException(status_code=500, detail="大模型调用失败，请检查API Key配置")

    return {
        "code": 0,
        "message": "success",
        "data": {
            "answer": answer,
            "knowledge_used": bool(knowledge_context),
            "source_chunks": []
        }
    }


@router.post("/question/stream")
async def process_question_stream(req: QuestionRequest):
    """处理面试问题 - 流式版本（SSE）

    与/question相同逻辑，但通过Server-Sent Events流式返回回答。
    """
    logger.info(f"流式处理面试问题: {req.question[:50]}...")

    # 第1步：知识库检索
    knowledge_context = ""
    if req.kb_id and req.kb_api_key:
        knowledge_context = get_relevant_knowledge(
            query=req.question,
            kb_id=req.kb_id,
            kb_api_key=req.kb_api_key
        )

    # 第2步：构建Prompt
    messages = build_messages(req.question, knowledge_context)

    # 第3步：流式返回
    async def generate():
        """SSE流式生成器"""
        try:
            # 发送初始状态
            yield f"data: {json.dumps({'type': 'status', 'message': '正在生成回答...'}, ensure_ascii=False)}\n\n"

            # 流式调用大模型
            for chunk in call_llm_stream(
                messages=messages,
                api_key=req.ark_api_key,
                model=req.model_id,
                temperature=0.7,
                max_tokens=1000
            ):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'knowledge_used': bool(knowledge_context)}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"流式生成异常: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': '生成失败，请重试'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
