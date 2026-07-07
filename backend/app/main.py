# FastAPI 应用入口
import uvicorn
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import BACKEND_HOST, BACKEND_PORT, FRONTEND_URL, DEBUG, ALLOWED_ORIGINS

# 数据库初始化
from app.database import engine, Base
from app.models import dialogue

Base.metadata.create_all(bind=engine)

# 日志配置 - 使用统一日志模块
from app.utils.logger import logger, log_api_request, log_api_error

app = FastAPI(
    title="面试虎 API",
    description="AI智能面试助手后端服务 - 提供知识库检索、大模型调用、配置管理等功能",
    version="1.0.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        log_api_request(path, method, response.status_code, duration_ms)
        return response
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        log_api_error(f"{method} {path}", exc)
        raise


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_api_error(f"全局异常 [{request.method} {request.url.path}]", exc)
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
from app.routes import health, config, search, generate, question, asr, transcript
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(config.router, prefix="/api", tags=["配置"])
app.include_router(search.router, prefix="/api", tags=["知识库检索"])
app.include_router(generate.router, prefix="/api", tags=["大模型生成"])
app.include_router(question.router, prefix="/api", tags=["问题处理"])
app.include_router(asr.router, prefix="/api", tags=["语音识别"])
app.include_router(transcript.router, prefix="/api", tags=["对话管理"])


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
