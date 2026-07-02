# 知识库检索路由
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.knowledge import get_relevant_knowledge

logger = logging.getLogger("interview-tiger")
router = APIRouter()


class SearchRequest(BaseModel):
    """知识库检索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="检索查询文本")
    kb_id: str = Field(..., description="知识库ID")
    kb_api_key: str = Field(..., description="知识库API Key (AK:SK)")
    top_k: int = Field(default=5, ge=1, le=10, description="返回结果数量")


@router.post("/search")
async def search_knowledge(req: SearchRequest):
    """检索知识库

    后端代理调用火山引擎RAG接口，返回相关文档片段。
    """
    logger.info(f"知识库检索: {req.query[:50]}...")

    try:
        knowledge = get_relevant_knowledge(
            query=req.query,
            kb_id=req.kb_id,
            kb_api_key=req.kb_api_key
        )

        if not knowledge:
            return {
                "code": 0,
                "message": "未找到相关知识",
                "data": {"chunks": []}
            }

        return {
            "code": 0,
            "message": "success",
            "data": {
                "chunks": [
                    {"content": knowledge, "score": 0.85, "doc_name": "知识库文档"}
                ]
            }
        }
    except Exception as e:
        logger.error(f"知识库检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"知识库检索失败: {str(e)}")
