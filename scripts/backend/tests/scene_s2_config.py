from utils.http_client import ApiClient
from logger import TestLogger


logger = TestLogger()
client = ApiClient()


def run():
    logger.info("=== 场景S2: 配置管理 ===")
    
    step = 1
    
    logger.step(step, "GET /api/config - 获取当前配置")
    http_code, business_code, data, _ = client.get("/api/config")
    
    if http_code != 200:
        logger.fatal(f"获取配置失败，HTTP状态码: {http_code}")
    if business_code != 0:
        logger.fatal(f"获取配置失败，业务状态码: {business_code}")
    
    required_fields = ["ark_api_key_configured", "kb_id", "model_id"]
    if "data" in data:
        for field in required_fields:
            if field not in data["data"]:
                logger.error(f"响应缺失字段: {field}")
            else:
                logger.success(f"字段验证通过: {field}")
    else:
        logger.error("响应缺失 data 字段")
    
    step += 1
    
    logger.step(step, "POST /api/config - 参数校验: 缺失 ark_api_key")
    http_code, business_code, data, _ = client.post("/api/config", {
        "kb_id": "test_kb",
        "model_id": "test_model"
    })
    
    if http_code == 400:
        logger.success("参数校验通过: 正确返回400")
    else:
        logger.error(f"参数校验失败，期望400，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/config - 参数校验: 缺失 kb_id")
    http_code, business_code, data, _ = client.post("/api/config", {
        "ark_api_key": "test_key_1234567890",
        "model_id": "test_model"
    })
    
    if http_code == 400:
        logger.success("参数校验通过: 正确返回400")
    else:
        logger.error(f"参数校验失败，期望400，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/config - 参数校验: API Key格式无效")
    http_code, business_code, data, _ = client.post("/api/config", {
        "ark_api_key": "short",
        "kb_id": "test_kb"
    })
    
    if http_code == 400:
        logger.success("参数校验通过: 正确返回400")
    else:
        logger.error(f"参数校验失败，期望400，实际: {http_code}")
    
    logger.success("场景S2完成: 配置管理测试通过")
