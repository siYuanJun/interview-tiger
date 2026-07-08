"""从前置接口返回值中提取数据"""


def extract_first_doc_id(list_response: dict) -> str:
    """从 list 接口返回值中提取第一个文档的 doc_id"""
    data = list_response.get("data", [])
    if not data:
        raise ValueError("文档列表为空，无法提取 doc_id")
    return data[0]["doc_id"]


def extract_first_filename(list_response: dict) -> str:
    """从 list 接口返回值中提取第一个文档的文件名"""
    data = list_response.get("data", [])
    if not data:
        raise ValueError("文档列表为空，无法提取 filename")
    return data[0]["doc_name"]


def extract_total_chunks(stats_response: dict) -> int:
    """从 stats 接口返回值中提取总切片数"""
    return stats_response.get("data", {}).get("total_chunks", 0)


def extract_chunk_count(upload_response: dict) -> int:
    """从 upload 接口返回值中提取上传的切片数"""
    data = upload_response.get("data", [])
    if not data:
        return 0
    return data[0].get("chunks", 0)


def count_search_results(search_response: dict) -> int:
    """统计检索返回的片段数"""
    return len(search_response.get("data", {}).get("chunks", []))
