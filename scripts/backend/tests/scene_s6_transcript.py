from utils.http_client import ApiClient
from logger import TestLogger


logger = TestLogger()
client = ApiClient()


def run():
    logger.info("=== 场景S6: 对话转录 ===")
    
    step = 1
    
    logger.step(step, "POST /api/transcript - 参数校验: 缺失 text")
    http_code, business_code, data, _ = client.post("/api/transcript", {
        "session_id": "test_session"
    })
    
    if http_code == 422:
        logger.success("参数校验通过: 正确返回422")
    else:
        logger.error(f"参数校验失败，期望422，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/transcript - 参数校验: text长度超限")
    http_code, business_code, data, _ = client.post("/api/transcript", {
        "text": "a" * 3000
    })
    
    if http_code == 422:
        logger.success("参数校验通过: 正确返回422")
    else:
        logger.error(f"参数校验失败，期望422，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "POST /api/transcript - 正常请求: 有效问题")
    http_code, business_code, data, _ = client.post("/api/transcript", {
        "text": "什么是Python？",
        "session_id": "test_session_001"
    })
    
    if http_code == 200 and business_code == 0:
        logger.success("请求成功")
        if "data" in data:
            required_fields = ["id", "question", "is_valid"]
            for field in required_fields:
                if field in data["data"]:
                    logger.success(f"字段验证通过: {field}")
                else:
                    logger.error(f"响应缺失字段: {field}")
    else:
        logger.error(f"请求失败，HTTP: {http_code}, 业务: {business_code}")
    
    step += 1
    
    logger.step(step, "POST /api/transcript - 正常请求: 无效问题")
    http_code, business_code, data, _ = client.post("/api/transcript", {
        "text": "哈哈哈哈",
        "session_id": "test_session_001"
    })
    
    if http_code == 200:
        logger.info(f"请求完成，业务状态码: {business_code}")
    else:
        logger.error(f"请求失败，HTTP: {http_code}")
    
    logger.success("场景S6完成: 对话转录测试通过")
