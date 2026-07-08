import os
import sys
import importlib
from datetime import datetime
from config import ALL_SCENES, P0_SCENES
from logger import TestLogger


logger = TestLogger()


def run_scene(scene_name):
    try:
        module = importlib.import_module(scene_name.replace(".py", ""))
        module.run()
        return True
    except Exception as e:
        logger.error(f"场景执行异常: {scene_name} - {str(e)}")
        return False


def main():
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("面试虎后端接口回归测试")
    logger.info(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    scenes = ALL_SCENES
    
    if len(sys.argv) > 1 and sys.argv[1] == "--p0":
        scenes = P0_SCENES
        logger.info("运行模式: 仅P0场景")
    else:
        logger.info("运行模式: 全量回归测试")
    
    logger.info(f"场景数量: {len(scenes)}")
    logger.info(f"场景列表: {scenes}")
    logger.info("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for idx, scene_name in enumerate(scenes, 1):
        logger.info(f"\n[{idx}/{len(scenes)}] 执行场景: {scene_name}")
        if run_scene(scene_name):
            success_count += 1
        else:
            fail_count += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    logger.info(f"总场景数: {len(scenes)}")
    logger.info(f"通过: {success_count}")
    logger.info(f"失败: {fail_count}")
    logger.info(f"耗时: {duration:.2f} 秒")
    logger.info(f"日志文件: {logger.get_log_file()}")
    
    if fail_count > 0:
        logger.error("测试未全部通过")
        sys.exit(1)
    else:
        logger.success("所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
