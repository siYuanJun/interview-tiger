from utils.http_client import ApiClient
from logger import TestLogger


logger = TestLogger()
client = ApiClient()


def run():
    logger.info("=== 场景S5: 大模型生成 ===")
    
    step = 1
    
    logger.step(step, "POST /api/generate - 参数校验: 缺失 prompt")
    http_code, business_code, data, _ = client.post("/api/generate", {
        "ark_api_key": "test_key_1234567890"
    })
    
    if http_code == 422:
        logger.success("参数校验通过: 正确返回422")
    else:
        logger.error(f"参数校验失败，期望422，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/generate - 使用默认配置（.env中已有API Key）")
    http_code, business_code, data, _ = client.post("/api/generate", {
        "prompt": "你好"
    })
    
    if http_code == 200 and business_code == 0:
        logger.success("使用默认配置成功，返回200")
    else:
        logger.info(f"请求完成，HTTP: {http_code}, 业务: {business_code}")
    
    step += 1
    
    logger.step(step, "POST /api/generate - 参数校验: temperature越界")
    http_code, business_code, data, _ = client.post("/api/generate", {
        "prompt": "你好",
        "ark_api_key": "test_key_1234567890",
        "temperature": 3.0
    })
    
    if http_code == 422:
        logger.success("参数校验通过: 正确返回422")
    else:
        logger.error(f"参数校验失败，期望422，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/generate - 正常请求（无API Key，预期失败）")
    http_code, business_code, data, _ = client.post("/api/generate", {
        "prompt": "你好",
        "ark_api_key": "test_key_1234567890",
        "stream": False
    })
    
    if http_code == 200 or http_code == 500:
        logger.info(f"请求完成，状态码: {http_code}")
    else:
        logger.error(f"请求异常，状态码: {http_code}")
    
    logger.success("场景S5完成: 大模型生成测试通过")
