"""场景 S1：健康检查 + 初始状态基线"""
import sys
from logging import Logger

from config import BASE_URL
from utils.http_client import ApiClient


def run(client: ApiClient, logger: Logger) -> bool:
    logger.info("")
    logger.info("=" * 60)
    logger.info("  场景 S1：健康检查 + 初始状态基线")
    logger.info("=" * 60)

    # ---- Step 1: 健康检查 ----
    logger.info("")
    logger.info("  [Step 1] 健康检查 GET /api/health")
    code, data, elapsed = client.get("/api/health")
    if code != 200 or data.get("code") != 0:
        logger.error("  ❌ 致命：服务健康检查失败！")
        sys.exit(1)
    logger.info(f"  ✅ 服务健康: {data['data']['service']} v{data['data']['version']}")

    # ---- Step 2: 获取初始统计 ----
    logger.info("")
    logger.info("  [Step 2] 初始统计 GET /api/local_kb/stats")
    code, data, elapsed = client.get("/api/local_kb/stats")
    if code != 200 or data.get("code") not in (0, -1):
        logger.error(f"  ❌ 致命：获取统计失败！code={code}")
        sys.exit(1)
    client.extracted["initial_stats"] = data
    logger.info(f"  ✅ 初始统计: {data.get('data', {})}")

    # ---- Step 3: 获取初始文档列表 ----
    logger.info("")
    logger.info("  [Step 3] 初始文档列表 GET /api/local_kb/list")
    code, data, elapsed = client.get("/api/local_kb/list")
    if code != 200 or data.get("code") != 0:
        logger.error(f"  ❌ 致命：获取列表失败！code={code}")
        sys.exit(1)
    initial_docs = data.get("data", [])
    logger.info(f"  ✅ 初始文档数: {len(initial_docs)}")
    for doc in initial_docs:
        logger.info(f"     - {doc.get('doc_name')} (chunks: {doc.get('chunks')})")

    logger.info("")
    logger.info("  🏁 场景 S1 完成")

    return True
