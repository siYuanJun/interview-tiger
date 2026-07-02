# 知识库检索路由
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.knowledge import get_relevant_knowledge
from config import KB_ID, KB_API_KEY

logger = logging.getLogger("interview-tiger")
router = APIRouter()


class SearchRequest(BaseModel):
    """知识库检索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="检索查询文本")
    kb_id: str = Field(default="", description="知识库ID（留空则使用.env配置）")
    kb_api_key: str = Field(default="", description="知识库API Key（留空则使用.env配置，AK:SK格式）")
    top_k: int = Field(default=5, ge=1, le=10, description="返回结果数量")


@router.post("/search")
async def search_knowledge(req: SearchRequest):
    """检索知识库

    后端代理调用火山引擎RAG接口，返回相关文档片段。
    """
    logger.info(f"知识库检索: {req.query[:50]}...")

    # 解析配置：前端传入优先，否则使用.env默认值
    kb_id = req.kb_id or KB_ID
    kb_api_key = req.kb_api_key or KB_API_KEY

    # 验证配置
    if not kb_id:
        raise HTTPException(status_code=400, detail="KB_ID未配置，请在.env或请求中提供")
    if not kb_api_key:
        raise HTTPException(status_code=400, detail="KB_API_KEY未配置，请在.env或请求中提供")

    try:
        knowledge = get_relevant_knowledge(
            query=req.query,
            kb_id=kb_id,
            kb_api_key=kb_api_key
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
