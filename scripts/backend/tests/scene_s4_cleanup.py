"""场景 S4：清理（删除文档 + 验证删除 + 清空知识库）"""
import sys
from logging import Logger

from utils.http_client import ApiClient


def run(client: ApiClient, logger: Logger) -> bool:
    logger.info("")
    logger.info("=" * 60)
    logger.info("  场景 S4：清理知识库")
    logger.info("=" * 60)

    doc_id = client.extracted.get("upload_doc_id", "")
    filename = client.extracted.get("upload_filename", "")

    # ---- Step 1: 删除单个文档 ----
    logger.info("")
    logger.info(f"  [Step 1] 删除文档 DELETE /api/local_kb/delete/{doc_id}")
    code, data, elapsed = client.delete(f"/api/local_kb/delete/{doc_id}")
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 删除失败！code={code}, message={data.get('message')}")
        sys.exit(1)

    deleted_chunks = data.get("data", {}).get("chunks_deleted", 0)
    logger.info(f"  ✅ 删除成功: {data.get('message')} (删除了 {deleted_chunks} 个切片)")

    # ---- Step 2: 验证删除 ----
    logger.info("")
    logger.info("  [Step 2] 验证文档已从列表中移除 GET /api/local_kb/list")
    code, data, elapsed = client.get("/api/local_kb/list")
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 获取列表失败")
        sys.exit(1)

    docs = data.get("data", [])
    still_exists = any(d.get("doc_id") == doc_id for d in docs)
    if still_exists:
        logger.error(f"  ❌ 致命：删除后文档仍在列表中！doc_id={doc_id}")
        sys.exit(1)
    logger.info(f"  ✅ 文档已从列表移除 (当前 {len(docs)} 个文档)")

    # ---- Step 3: 验证下载 404 ----
    logger.info("")
    logger.info(f"  [Step 3] 验证原文件不可下载 GET /api/local_kb/download/{doc_id}")
    code, content, elapsed = client.download(f"/api/local_kb/download/{doc_id}")
    if code != 404:
        logger.error(f"  ❌ 预期 404，实际 {code}")
        sys.exit(1)
    logger.info("  ✅ 返回 404，原始文件已清理")

    # ---- Step 4: 清空知识库 ----
    logger.info("")
    logger.info("  [Step 4] 清空知识库 DELETE /api/local_kb/clear")
    code, data, elapsed = client.delete("/api/local_kb/clear")
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 清空失败")
        sys.exit(1)
    logger.info(f"  ✅ {data.get('message')}")

    # ---- Step 5: 验证清空 ----
    logger.info("")
    logger.info("  [Step 5] 验证知识库已清空 GET /api/local_kb/stats")
    code, data, elapsed = client.get("/api/local_kb/stats")
    if code != 200 or data.get("code") not in (0, -1):
        logger.error(f"  ❌ 获取统计失败")
        sys.exit(1)

    total = data.get("data", {}).get("total_chunks", 0)
    logger.info(f"  ✅ 清空后总切片数: {total}")
    if total != 0:
        logger.error(f"  ❌ 清空后切片数不為 0")
        sys.exit(1)

    logger.info("")
    logger.info("  🏁 场景 S4 完成")

    return True
