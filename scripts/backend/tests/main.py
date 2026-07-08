"""主入口：按序执行所有测试场景"""
import sys
import time

from config import BASE_URL, REQUEST_TIMEOUT
from logger import setup_logger
from utils.http_client import ApiClient


def main():
    # 初始化日志
    logger = setup_logger()

    logger.info("")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + "  面试虎 - 本地知识库接口测试".center(52) + "║")
    logger.info("╠" + "═" * 58 + "╣")
    logger.info(f"║  BASE_URL: {BASE_URL}".ljust(59) + "║")
    logger.info(f"║  超时: {REQUEST_TIMEOUT}s".ljust(59) + "║")
    logger.info("╚" + "═" * 58 + "╝")

    # 创建客户端
    client = ApiClient(BASE_URL, logger, timeout=REQUEST_TIMEOUT)

    total_start = time.time()

    scenes = [
        ("S1", "scene_s1_health", "健康检查 + 初始状态基线"),
        ("S2", "scene_s2_upload", "上传真实面试知识库文件"),
        ("S3", "scene_s3_verify", "验证上传结果"),
        ("S4", "scene_s4_cleanup", "清理知识库"),
    ]

    results = {}
    for scene_id, module_name, description in scenes:
        logger.info(f"\n{'#' * 60}")
        logger.info(f"#  执行场景 [{scene_id}] {description}")
        logger.info(f"{'#' * 60}")

        try:
            mod = __import__(module_name)
            scene_start = time.time()
            mod.run(client, logger)
            elapsed = time.time() - scene_start
            results[scene_id] = ("PASS", elapsed)
            logger.info(f"\n  ✅ [{scene_id}] 通过 ({elapsed:.1f}s)")
        except SystemExit as e:
            if e.code == 0:
                results[scene_id] = ("PASS", 0)
            else:
                results[scene_id] = ("FATAL", 0)
                logger.error(f"\n  ❌ [{scene_id}] 致命错误，测试终止")
                break
        except Exception as e:
            results[scene_id] = ("ERROR", 0)
            logger.error(f"\n  ❌ [{scene_id}] 异常: {e}")
            break

    # 汇总报告
    total_elapsed = time.time() - total_start
    logger.info("")
    logger.info("=" * 60)
    logger.info("                     测试结果汇总")
    logger.info("=" * 60)
    passed = sum(1 for r in results.values() if r[0] == "PASS")
    failed = len(results) - passed
    for scene_id, module_name, description in scenes:
        if scene_id in results:
            status, elapsed = results[scene_id]
            icon = "✅" if status == "PASS" else "❌"
            logger.info(f"  {icon} [{scene_id}] {description} ({elapsed:.1f}s)")
        else:
            logger.info(f"  ⏭️ [{scene_id}] {description} (未执行)")

    logger.info(f"\n  通过: {passed}/{len(scenes)}  失败: {failed}/{len(scenes)}")
    logger.info(f"  总耗时: {total_elapsed:.1f}s")
    logger.info("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
