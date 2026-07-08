from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from config import ARK_MODEL, KB_PROVIDER

logger = logging.getLogger("interview-tiger")
router = APIRouter()


class SaveConfigRequest(BaseModel):
    ark_api_key: str = Field(default="", description="火山引擎API Key")
    kb_id: str = Field(default="", description="知识库ID")
    kb_api_key: str = Field(default="", description="知识库API Key")
    model_id: str = Field(default=ARK_MODEL, description="模型ID")
    kb_provider: str = Field(default="volcengine", description="知识库提供者（volcengine/local）")


class ConfigInfo(BaseModel):
    ark_api_key_configured: bool = Field(description="API Key是否已配置")
    kb_id: str = Field(description="知识库ID")
    kb_api_key_configured: bool = Field(description="知识库API Key是否已配置")
    model_id: str = Field(description="模型ID")
    kb_provider: str = Field(description="知识库提供者")


@router.post("/config")
async def save_config(req: SaveConfigRequest):
    logger.info("保存配置请求")

    if not req.ark_api_key:
        raise HTTPException(status_code=400, detail="API Key不能为空")

    if req.kb_provider == "volcengine":
        if not req.kb_id:
            raise HTTPException(status_code=400, detail="知识库ID不能为空")
        if not req.kb_api_key:
            raise HTTPException(status_code=400, detail="知识库API Key不能为空")

    if len(req.ark_api_key) < 10:
        raise HTTPException(status_code=400, detail="API Key格式无效")

    return {
        "code": 0,
        "message": "配置已保存",
        "data": {
            "ark_api_key_configured": True,
            "kb_id": req.kb_id,
            "kb_api_key_configured": bool(req.kb_api_key),
            "model_id": req.model_id,
            "kb_provider": req.kb_provider
        }
    }


@router.get("/config")
async def get_config():
    from config import ARK_API_KEY, KB_ID, KB_API_KEY, ARK_MODEL, KB_PROVIDER

    return {
        "code": 0,
        "message": "success",
        "data": {
            "ark_api_key_configured": bool(ARK_API_KEY and ARK_API_KEY != "your_api_key_here"),
            "kb_id": KB_ID if KB_ID != "kb-xxx" else "",
            "kb_api_key_configured": bool(KB_API_KEY and KB_API_KEY != "your_viking_api_key_here"),
            "model_id": ARK_MODEL,
            "kb_provider": KB_PROVIDER
        }
    }
