from utils.http_client import ApiClient
from logger import TestLogger


logger = TestLogger()
client = ApiClient()


def run():
    logger.info("=== 场景S1: 健康检查 ===")
    
    step = 1
    
    logger.step(step, "GET /api/health - 服务健康检查")
    http_code, business_code, data, _ = client.get("/api/health")
    
    if http_code != 200:
        logger.fatal(f"健康检查失败，HTTP状态码: {http_code}")
    if business_code != 0:
        logger.fatal(f"健康检查失败，业务状态码: {business_code}")
    
    required_fields = ["status", "service", "version"]
    if "data" in data:
        for field in required_fields:
            if field not in data["data"]:
                logger.error(f"响应缺失字段: {field}")
            else:
                logger.success(f"字段验证通过: {field}={data['data'][field]}")
    else:
        logger.error("响应缺失 data 字段")
    
    logger.success("场景S1完成: 健康检查通过")
