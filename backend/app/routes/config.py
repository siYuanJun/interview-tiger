# 配置管理路由
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from config import ARK_MODEL

logger = logging.getLogger("interview-tiger")
router = APIRouter()


class SaveConfigRequest(BaseModel):
    """保存配置请求"""
    ark_api_key: str = Field(default="", description="火山引擎API Key")
    kb_id: str = Field(default="", description="知识库ID")
    model_id: str = Field(default=ARK_MODEL, description="模型ID")


class ConfigInfo(BaseModel):
    """配置信息（脱敏）"""
    ark_api_key_configured: bool = Field(description="API Key是否已配置")
    kb_id: str = Field(description="知识库ID")
    model_id: str = Field(description="模型ID")


@router.post("/config")
async def save_config(req: SaveConfigRequest):
    """保存配置并验证有效性

    接收前端传来的API Key、知识库ID和模型ID配置。
    后端仅做转发验证，实际存储在前端localStorage。
    """
    logger.info("保存配置请求")

    if not req.ark_api_key:
        raise HTTPException(status_code=400, detail="API Key不能为空")

    if not req.kb_id:
        raise HTTPException(status_code=400, detail="知识库ID不能为空")

    # 验证API Key格式（基本检查）
    if len(req.ark_api_key) < 10:
        raise HTTPException(status_code=400, detail="API Key格式无效")

    return {
        "code": 0,
        "message": "配置已保存",
        "data": {
            "ark_api_key_configured": True,
            "kb_id": req.kb_id,
            "model_id": req.model_id
        }
    }


@router.get("/config")
async def get_config():
    """获取当前配置状态（返回脱敏信息）"""
    from config import ARK_API_KEY, KB_ID, ARK_MODEL

    return {
        "code": 0,
        "message": "success",
        "data": {
            "ark_api_key_configured": bool(ARK_API_KEY and ARK_API_KEY != "your_api_key_here"),
            "kb_id": KB_ID if KB_ID != "kb-xxx" else "",
            "model_id": ARK_MODEL
        }
    }
