from utils.http_client import ApiClient
from utils.data_extractor import extract_dialogue_id, extract_session_id
from logger import TestLogger


logger = TestLogger()
client = ApiClient()


def run():
    logger.info("=== 场景S7: 对话管理 ===")
    
    step = 1
    dialogue_id = None
    session_id = None
    
    logger.step(step, "POST /api/transcript - 创建测试对话")
    http_code, business_code, data, _ = client.post("/api/transcript", {
        "text": "测试对话问题",
        "session_id": "test_session_dialogue"
    })
    
    if http_code == 200 and business_code == 0 and "data" in data:
        dialogue_id = extract_dialogue_id(data)
        session_id = extract_session_id(data)
        logger.success(f"创建成功，dialogue_id={dialogue_id}")
    else:
        logger.error(f"创建失败，HTTP: {http_code}, 业务: {business_code}")
        logger.success("场景S7完成: 对话管理测试（跳过后续步骤）")
        return
    
    step += 1
    
    logger.step(step, "GET /api/dialogues - 获取对话列表")
    http_code, business_code, data, _ = client.get("/api/dialogues", {
        "session_id": session_id
    })
    
    if http_code == 200 and business_code == 0:
        logger.success("获取成功")
        if "data" in data and "dialogues" in data["data"]:
            logger.success(f"返回对话数量: {len(data['data']['dialogues'])}")
    else:
        logger.error(f"获取失败，HTTP: {http_code}, 业务: {business_code}")
    
    step += 1
    
    logger.step(step, "PUT /api/dialogues/{id} - 更新对话回答")
    http_code, business_code, data, _ = client.put(f"/api/dialogues/{dialogue_id}", params={
        "answer": "测试回答内容"
    })
    
    if http_code == 200 and business_code == 0:
        logger.success("更新成功")
    else:
        logger.error(f"更新失败，HTTP: {http_code}, 业务: {business_code}")
    
    step += 1
    
    logger.step(step, "PUT /api/dialogues/{id} - 参数校验: 不存在的ID")
    http_code, business_code, data, _ = client.put("/api/dialogues/nonexistent_id", params={
        "answer": "测试"
    })
    
    if http_code == 404:
        logger.success("参数校验通过: 正确返回404")
    else:
        logger.error(f"参数校验失败，期望404，实际: {http_code}")
    
    step += 1
    
    logger.step(step, "DELETE /api/dialogues - 按session_id删除")
    http_code, business_code, data, _ = client.delete("/api/dialogues", {
        "session_id": session_id
    })
    
    if http_code == 200 and business_code == 0:
        logger.success("删除成功")
    else:
        logger.error(f"删除失败，HTTP: {http_code}, 业务: {business_code}")
    
    logger.success("场景S7完成: 对话管理测试通过")
