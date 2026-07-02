# 大模型生成路由
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
from app.services.llm import call_llm, call_llm_stream

logger = logging.getLogger("interview-tiger")
router = APIRouter()


class GenerateRequest(BaseModel):
    """大模型生成请求"""
    prompt: str = Field(..., min_length=1, max_length=5000, description="完整Prompt文本")
    ark_api_key: str = Field(..., description="火山引擎API Key")
    model_id: str = Field(default="doubao-seed-2-1-pro-260628", description="模型ID")
    stream: bool = Field(default=False, description="是否流式输出")
    temperature: float = Field(default=0.7, ge=0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="最大输出token数")


@router.post("/generate")
async def generate_answer(req: GenerateRequest):
    """大模型生成回答 - 非流式版本"""
    logger.info(f"大模型生成请求 (stream={req.stream})")

    messages = [{"role": "user", "content": req.prompt}]

    answer = call_llm(
        messages=messages,
        api_key=req.ark_api_key,
        model=req.model_id,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        stream=False
    )

    if answer is None:
        raise HTTPException(status_code=500, detail="大模型调用失败，请检查API Key配置")

    return {
        "code": 0,
        "message": "success",
        "data": {"answer": answer}
    }


@router.post("/generate/stream")
async def generate_answer_stream(req: GenerateRequest):
    """大模型生成回答 - 流式SSE版本"""
    logger.info(f"大模型流式生成请求")

    messages = [{"role": "user", "content": req.prompt}]

    async def generate():
        try:
            for chunk in call_llm_stream(
                messages=messages,
                api_key=req.ark_api_key,
                model=req.model_id,
                temperature=req.temperature,
                max_tokens=req.max_tokens
            ):
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"流式生成异常: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
