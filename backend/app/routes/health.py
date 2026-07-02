# 健康检查路由
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """服务健康检查

    返回服务运行状态和基本信息。
    可用于 Docker 健康检查或前端连接测试。
    """
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "status": "healthy",
            "service": "面试虎 API",
            "version": "1.0.0"
        }
    }
