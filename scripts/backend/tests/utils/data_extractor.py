def extract_field(response_data, field_path, default=None):
    """从响应数据中提取字段"""
    if not response_data or not isinstance(response_data, dict):
        return default
    
    if "data" not in response_data:
        return default
    
    data = response_data["data"]
    
    keys = field_path.split(".")
    result = data
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        elif isinstance(result, list) and key.isdigit():
            idx = int(key)
            if idx < len(result):
                result = result[idx]
            else:
                return default
        else:
            return default
    
    return result


def extract_dialogue_id(response_data):
    return extract_field(response_data, "id")


def extract_session_id(response_data):
    return extract_field(response_data, "session_id")


def extract_answer(response_data):
    return extract_field(response_data, "answer")
