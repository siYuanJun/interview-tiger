# FastAPI 应用入口
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import BACKEND_HOST, BACKEND_PORT, FRONTEND_URL, DEBUG

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interview-tiger")

app = FastAPI(
    title="面试虎 API",
    description="AI智能面试助手后端服务 - 提供知识库检索、大模型调用、配置管理等功能",
    version="1.0.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )


# 自定义 HTTP 异常处理
from fastapi.exceptions import HTTPException as FastAPIHTTPException

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


# 注册路由
from app.routes import health, config, search, generate, question, asr
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(config.router, prefix="/api", tags=["配置"])
app.include_router(search.router, prefix="/api", tags=["知识库检索"])
app.include_router(generate.router, prefix="/api", tags=["大模型生成"])
app.include_router(question.router, prefix="/api", tags=["问题处理"])
app.include_router(asr.router, prefix="/api", tags=["语音识别"])


@app.get("/")
async def root():
    """API根路径信息"""
    return {
        "name": "面试虎 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=DEBUG
    )
