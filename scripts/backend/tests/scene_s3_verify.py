"""场景 S3：验证上传结果（列表/搜索/下载/统计）"""
import sys
from logging import Logger

from config import SEARCH_QUERY, SEARCH_TOP_K
from utils.http_client import ApiClient
from utils.data_extractor import (
    extract_total_chunks,
    count_search_results,
)


def run(client: ApiClient, logger: Logger) -> bool:
    logger.info("")
    logger.info("=" * 60)
    logger.info("  场景 S3：验证上传结果")
    logger.info("=" * 60)

    doc_id = client.extracted.get("upload_doc_id", "")
    filename = client.extracted.get("upload_filename", "")
    expected_chunks = client.extracted.get("upload_chunks", 0)

    if not doc_id:
        logger.error("  ❌ 致命：未找到已上传的 doc_id，请先运行场景 S2")
        sys.exit(1)

    # ---- Step 1: 文档列表验证 ----
    logger.info("")
    logger.info("  [Step 1] 验证文档出现在列表中 GET /api/local_kb/list")
    code, data, elapsed = client.get("/api/local_kb/list")
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 获取列表失败！code={code}")
        sys.exit(1)

    docs = data.get("data", [])
    found = None
    for doc in docs:
        if doc.get("doc_id") == doc_id:
            found = doc
            break

    if not found:
        logger.error(f"  ❌ 致命：列表中未找到已上传的文档 doc_id={doc_id}")
        logger.info(f"  当前列表: {[d['doc_name'] for d in docs]}")
        sys.exit(1)

    logger.info(f"  ✅ 文档在列表中: {found['doc_name']}")
    logger.info(f"     doc_id: {found['doc_id']}")
    logger.info(f"     chunks: {found['chunks']}")
    if found.get("file_size_bytes"):
        logger.info(f"     file_size: {found['file_size_bytes']} bytes")

    # ---- Step 2: 知识库检索 ----
    logger.info("")
    logger.info(f"  [Step 2] 知识库检索 POST /api/local_kb/search query='{SEARCH_QUERY}'")
    code, data, elapsed = client.post("/api/local_kb/search", json={
        "query": SEARCH_QUERY,
        "top_k": SEARCH_TOP_K
    })
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 检索失败！code={code}, message={data.get('message')}")
        sys.exit(1)

    chunks = data.get("data", {}).get("chunks", [])
    result_count = len(chunks)
    logger.info(f"  ✅ 检索结果数: {result_count}")

    if result_count == 0:
        logger.error("  ❌ 致命：检索结果为空，向量索引可能未生效")
        sys.exit(1)

    for i, chunk in enumerate(chunks[:3]):
        content_preview = chunk.get("content", "")[:80].replace("\n", "\\n")
        logger.info(
            f"     [{i+1}] score={chunk.get('score'):.4f} "
            f"doc='{chunk.get('doc_name', '')}' "
            f"| '{content_preview}...'"
        )

    # ---- Step 3: 下载原始文件 ----
    logger.info("")
    logger.info(f"  [Step 3] 下载原始文件 GET /api/local_kb/download/{doc_id}")
    code, content, elapsed = client.download(f"/api/local_kb/download/{doc_id}")
    if code != 200:
        logger.error(f"  ❌ 下载失败！code={code}")
        sys.exit(1)

    download_size = len(content)
    logger.info(f"  ✅ 下载成功: {download_size} bytes")

    # 检查文件内容非空
    if download_size == 0:
        logger.error("  ❌ 致命：下载的文件内容为空！")
        sys.exit(1)

    # 检查是否为 markdown 内容
    try:
        text_content = content.decode("utf-8")
        preview = text_content[:100].replace("\n", "\\n")
        logger.info(f"     内容预览: '{preview}...'")
    except Exception:
        logger.info("     内容为二进制数据")

    # ---- Step 4: 统计验证 ----
    logger.info("")
    logger.info("  [Step 4] 验证统计数据 GET /api/local_kb/stats")
    code, data, elapsed = client.get("/api/local_kb/stats")
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 获取统计失败！code={code}")
        sys.exit(1)

    total = extract_total_chunks(data)
    logger.info(f"  ✅ 当前总切片数: {total}")
    logger.info(f"     embedding_model: {data.get('data', {}).get('embedding_model', 'N/A')}")
    logger.info(f"     data_dir: {data.get('data', {}).get('data_dir', 'N/A')}")

    if total <= 0:
        logger.error("  ❌ 致命：切片总数为 0")
        sys.exit(1)

    logger.info("")
    logger.info("  🏁 场景 S3 完成")

    return True
