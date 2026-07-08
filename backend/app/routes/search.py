import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.utils.kb_provider import get_knowledge_provider, get_kb_provider_type
from app.utils.logger import logger
from config import KB_ID, KB_API_KEY

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="检索查询文本")
    kb_id: str = Field(default="", description="知识库ID（留空则使用.env配置）")
    kb_api_key: str = Field(default="", description="知识库API Key（留空则使用.env配置）")
    kb_provider: str = Field(default="", description="知识库提供者（volcengine/local）")
    top_k: int = Field(default=5, ge=1, le=10, description="返回结果数量")


@router.post("/search")
async def search_knowledge(req: SearchRequest):
    logger.info(f"知识库检索: {req.query[:50]}..., 提供者: {req.kb_provider or '默认'}")

    provider_type = get_kb_provider_type(req.kb_provider)
    
    if provider_type == "local":
        provider = get_knowledge_provider("local")
        result = provider.search_with_details(req.query, top_k=req.top_k)
        
        if not result.get("chunks"):
            return {
                "code": 0,
                "message": "未找到相关知识",
                "data": {"chunks": []}
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    else:
        kb_id = req.kb_id or KB_ID
        kb_api_key = req.kb_api_key or KB_API_KEY

        if not kb_id:
            raise HTTPException(status_code=400, detail="KB_ID未配置，请在.env或请求中提供")
        if not kb_api_key:
            raise HTTPException(status_code=400, detail="KB_API_KEY未配置，请在.env或请求中提供")

        try:
            provider = get_knowledge_provider("volcengine", kb_id, kb_api_key)
            result = provider.search_with_details(req.query, top_k=req.top_k)
            
            if not result.get("chunks"):
                return {
                    "code": 0,
                    "message": "未找到相关知识",
                    "data": {"chunks": []}
                }
            
            return {
                "code": 0,
                "message": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"知识库检索失败: {e}")
            raise HTTPException(status_code=500, detail=f"知识库检索失败: {str(e)}")
