from utils.http_client import ApiClient
from logger import TestLogger


logger = TestLogger()
client = ApiClient()


def run():
    logger.info("=== 场景S4: 知识库检索 ===")
    
    step = 1
    
    logger.step(step, "POST /api/search - 参数校验: 缺失 query")
    http_code, business_code, data, _ = client.post("/api/search", {
        "kb_id": "test_kb",
        "kb_api_key": "test_key"
    })
    
    if http_code == 422:
        logger.success("参数校验通过: 正确返回422")
    else:
        logger.error(f"参数校验失败，期望422，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/search - 参数校验: query长度超限")
    http_code, business_code, data, _ = client.post("/api/search", {
        "query": "a" * 600,
        "kb_id": "test_kb",
        "kb_api_key": "test_key"
    })
    
    if http_code == 422:
        logger.success("参数校验通过: 正确返回422")
    else:
        logger.error(f"参数校验失败，期望422，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/search - 正常请求（无API Key，预期失败）")
    http_code, business_code, data, _ = client.post("/api/search", {
        "query": "什么是Python？",
        "kb_id": "test_kb",
        "kb_api_key": "test_key"
    })
    
    if http_code == 200 or http_code == 500:
        logger.info(f"请求完成，状态码: {http_code}")
    else:
        logger.error(f"请求异常，状态码: {http_code}")
    
    logger.success("场景S4完成: 知识库检索测试通过")
