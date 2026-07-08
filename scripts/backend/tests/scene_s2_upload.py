"""场景 S2：上传真实面试知识库文件"""
import os
import sys
from logging import Logger
from pathlib import Path

from config import BASE_URL, TEST_FILE_PATH, CHUNK_SIZE, CHUNK_OVERLAP
from utils.http_client import ApiClient


def run(client: ApiClient, logger: Logger) -> bool:
    logger.info("")
    logger.info("=" * 60)
    logger.info("  场景 S2：上传文件到本地知识库")
    logger.info("=" * 60)

    # ---- Step 1: 检查文件是否存在 ----
    logger.info("")
    logger.info(f"  [Step 1] 检查测试文件: {TEST_FILE_PATH}")
    file_path = Path(TEST_FILE_PATH)
    if not file_path.exists():
        logger.error(f"  ❌ 致命：测试文件不存在: {TEST_FILE_PATH}")
        sys.exit(1)
    file_size = file_path.stat().st_size
    logger.info(f"  ✅ 文件存在: {file_path.name} ({file_size} bytes)")

    # ---- Step 2: 上传文件 ----
    logger.info("")
    logger.info("  [Step 2] 上传文件 POST /api/local_kb/upload")
    logger.info(f"  📎 chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}")

    with open(file_path, "rb") as f:
        files = {"files": (file_path.name, f, "text/markdown")}
        data = {
            "chunk_size": str(CHUNK_SIZE),
            "chunk_overlap": str(CHUNK_OVERLAP),
        }
        code, resp, elapsed = client.post(
            "/api/local_kb/upload", data=data, files=files
        )

    if code != 200 or resp.get("code") != 0:
        logger.error(f"  ❌ 致命：上传失败！code={code}, message={resp.get('message')}")
        sys.exit(1)

    uploaded = resp.get("data", [])
    if not uploaded:
        logger.error("  ❌ 致命：上传返回空数据！")
        sys.exit(1)

    first_file = uploaded[0]
    doc_id = first_file.get("doc_id", "")
    chunks = first_file.get("chunks", 0)
    filename = first_file.get("filename", "")

    client.extracted["upload_doc_id"] = doc_id
    client.extracted["upload_filename"] = filename
    client.extracted["upload_chunks"] = chunks

    logger.info(f"  ✅ 上传成功 | 耗时: {elapsed:.0f}ms")
    logger.info(f"     文件名: {filename}")
    logger.info(f"     doc_id: {doc_id}")
    logger.info(f"     切片数: {chunks}")

    logger.info("")
    logger.info("  🏁 场景 S2 完成")

    return True
