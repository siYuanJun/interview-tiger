from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path

from app.utils.kb_provider import get_knowledge_provider
from app.utils.logger import logger
from config import LOCAL_KB_ORIGINALS_DIR

router = APIRouter()


class UploadRequest(BaseModel):
    chunk_size: int = Field(default=500, ge=200, le=2000, description="切片大小")
    chunk_overlap: int = Field(default=50, ge=0, le=200, description="重叠大小")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="检索查询文本")
    top_k: int = Field(default=5, ge=1, le=10, description="返回结果数量")


@router.post("/local_kb/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    chunk_size: int = Query(500, ge=200, le=2000),
    chunk_overlap: int = Query(50, ge=0, le=200)
):
    logger.info(f"本地知识库上传请求: {len(files)} 个文件")
    
    provider = get_knowledge_provider("local")
    
    try:
        result = provider.upload(files, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        if result.get("code") != 0:
            raise HTTPException(status_code=500, detail=result.get("message", "上传失败"))
        
        return {
            "code": 0,
            "message": result.get("message", "上传成功"),
            "data": result.get("data", [])
        }
    except Exception as e:
        logger.error(f"本地知识库上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/local_kb/list")
async def list_documents():
    logger.info("获取本地知识库文档列表")
    
    provider = get_knowledge_provider("local")
    
    try:
        docs = provider.list_docs()
        return {
            "code": 0,
            "message": "success",
            "data": docs
        }
    except Exception as e:
        logger.error(f"获取本地知识库文档列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.delete("/local_kb/delete/{doc_id}")
async def delete_document(doc_id: str):
    logger.info(f"删除本地知识库文档: {doc_id}")
    
    provider = get_knowledge_provider("local")
    
    try:
        result = provider.delete_doc(doc_id)
        
        if result.get("code") != 0:
            raise HTTPException(status_code=404, detail=result.get("message", "删除失败"))
        
        return {
            "code": 0,
            "message": result.get("message", "删除成功"),
            "data": result.get("data", {})
        }
    except Exception as e:
        logger.error(f"删除本地知识库文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.delete("/local_kb/clear")
async def clear_knowledge_base():
    logger.info("清空本地知识库")
    
    provider = get_knowledge_provider("local")
    
    try:
        result = provider.clear()
        
        if result.get("code") != 0:
            raise HTTPException(status_code=500, detail=result.get("message", "清空失败"))
        
        return {
            "code": 0,
            "message": result.get("message", "清空成功"),
            "data": result.get("data", {})
        }
    except Exception as e:
        logger.error(f"清空本地知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空失败: {str(e)}")


@router.post("/local_kb/search")
async def search_local_kb(req: SearchRequest):
    logger.info(f"本地知识库检索: {req.query[:50]}...")
    
    provider = get_knowledge_provider("local")
    
    try:
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
        logger.error(f"本地知识库检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.get("/local_kb/stats")
async def get_kb_stats():
    logger.info("获取本地知识库统计信息")
    
    provider = get_knowledge_provider("local")
    
    try:
        result = provider.get_stats()
        
        if result.get("code") != 0:
            raise HTTPException(status_code=500, detail=result.get("message", "获取统计失败"))
        
        return {
            "code": 0,
            "message": "success",
            "data": result.get("data", {})
        }
    except Exception as e:
        logger.error(f"获取本地知识库统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/local_kb/download/{doc_id}")
async def download_document(doc_id: str):
    """下载知识库原始文件"""
    originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
    matches = list(originals_dir.glob(f"{doc_id}_*"))
    if not matches:
        raise HTTPException(status_code=404, detail="原始文件不存在")
    
    file_path = matches[0]
    original_name = file_path.name[len(doc_id) + 1:]
    
    ext = file_path.suffix.lower()
    mime_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".json": "application/json",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    media_type = mime_map.get(ext, "application/octet-stream")
    
    logger.info(f"下载原始文件: {original_name}")
    return FileResponse(file_path, filename=original_name, media_type=media_type)
