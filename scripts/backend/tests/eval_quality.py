"""RAG 质量评测脚本：切片质量 + 召回率
运行方式：cd scripts/backend/tests && ./venv/bin/python eval_quality.py
前置条件：已通过 run_all.sh 上传过测试文件
"""
import json
import sys
import requests
from pathlib import Path

BASE_URL = "http://localhost:8001"
TIMEOUT = 60

# ============================================================
# 1. 定义 Ground Truth（人工标注的查询-预期匹配内容关键词）
# ============================================================
GROUND_TRUTH = [
    {
        "query": "自我介绍",
        "expected_keywords": ["刘朝相", "全栈", "AI", "8年"],  # 至少出现 2 个算命中
        "min_results": 3,
    },
    {
        "query": "离职原因",
        "expected_keywords": ["业务调整", "团队被裁撤", "被动离职"],
        "min_results": 2,
    },
    {
        "query": "薪资谈判",
        "expected_keywords": ["薪资", "预算", "底线"],
        "min_results": 2,
    },
    {
        "query": "Python Django 微服务",
        "expected_keywords": [],  # 文档里没有，应该低分
        "min_results": 0,        # 不要求有结果
    },
    {
        "query": "全栈工程师",
        "expected_keywords": ["全栈", "Vue", "React"],
        "min_results": 2,
    },
]


def api_get(path):
    resp = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    return resp.json()

def api_post(path, body):
    resp = requests.post(f"{BASE_URL}{path}", json=body, timeout=TIMEOUT)
    return resp.json()

def upload_file(filepath):
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/api/local_kb/upload",
            files={"files": (Path(filepath).name, f, "text/markdown")},
            data={"chunk_size": "500", "chunk_overlap": "50"},
            timeout=TIMEOUT,
        )
    return resp.json()


def main():
    # 先清空，确保干净环境
    print("=" * 60)
    print("  RAG 质量评测")
    print("=" * 60)

    # 上传测试文件
    test_file = Path.home() / "Documents/个人信息/简历/简历内容/docs/知识库/面试知识库-整理版/01-自我介绍与核心必答题.md"
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        sys.exit(1)

    # 清空知识库
    print("\n[准备] 清空知识库...")
    api_get("/api/local_kb/clear")  # 可能空集合报错，忽略

    # 上传
    print(f"[准备] 上传测试文件: {test_file.name} ({test_file.stat().st_size} bytes)")
    result = upload_file(str(test_file))
    if result.get("code") != 0:
        print(f"❌ 上传失败: {result}")
        sys.exit(1)
    data = result["data"][0]
    chunks = data["chunks"]
    print(f"   ✅ 切片数: {chunks}")

    # ============================================================
    # Part 1: 切片质量分析
    # ============================================================
    print("\n" + "=" * 60)
    print("  Part 1: 切片质量分析")
    print("=" * 60)

    stats = api_get("/api/local_kb/stats")["data"]
    print(f"  总切片数: {stats['total_chunks']}")
    print(f"  模型: {stats['embedding_model']}")

    # 用搜索获取实际切片内容
    all_content = api_post("/api/local_kb/search", {"query": "自我介绍 离职 薪资 全栈", "top_k": 20})
    all_chunks = all_content.get("data", {}).get("chunks", [])

    if all_chunks:
        lengths = [len(c["content"]) for c in all_chunks]
        print(f"\n  切片长度分布:")
        print(f"    最小: {min(lengths)} 字符")
        print(f"    最大: {max(lengths)} 字符")
        print(f"    平均: {sum(lengths)/len(lengths):.0f} 字符")
        print(f"    中位: {sorted(lengths)[len(lengths)//2]} 字符")

        # 切片完整性检查
        full_breaks = 0
        partial_breaks = 0
        for c in all_chunks:
            content = c["content"].strip()
            if content.endswith(("\n\n", "---", "。", "？", "！")):
                full_breaks += 1
            else:
                partial_breaks += 1

        print(f"\n  切片边界完整性:")
        print(f"    自然断点（句尾/章节尾）: {full_breaks}/{len(all_chunks)}")
        print(f"    非自然断点（句中截断）: {partial_breaks}/{len(all_chunks)}")
        if partial_breaks > len(all_chunks) * 0.3:
            print(f"    ⚠️ 超过 30% 切片在句中截断，建议调大 chunk_size 或优化 separators")

        # 重叠度检查
        print(f"\n  配置参数:")
        print(f"    chunk_size: 500")
        print(f"    chunk_overlap: 50")
        print(f"    重叠比: {50/500*100:.0f}%")

    # ============================================================
    # Part 2: 召回率评测
    # ============================================================
    print("\n" + "=" * 60)
    print("  Part 2: 召回率评测")
    print("=" * 60)

    recall_hits = 0
    total_queries = len(GROUND_TRUTH)

    for i, gt in enumerate(GROUND_TRUTH):
        query = gt["query"]
        keywords = gt["expected_keywords"]
        min_results = gt["min_results"]

        result = api_post("/api/local_kb/search", {"query": query, "top_k": 5})
        chunks = result.get("data", {}).get("chunks", [])
        result_count = len(chunks)

        # 检查关键词命中
        all_text = " ".join(c["content"] for c in chunks)
        keyword_hits = sum(1 for kw in keywords if kw in all_text)

        if keywords:
            keyword_ratio = keyword_hits / len(keywords) if keywords else 1.0
        else:
            keyword_ratio = 1.0

        passed = result_count >= min_results and (keyword_ratio >= 0.5 or not keywords)

        icon = "✅" if passed else "❌"
        status = "PASS" if passed else "FAIL"

        top_scores = [f"{c['score']:.4f}" for c in chunks[:3]]
        scores_str = ", ".join(top_scores) if top_scores else "N/A"

        print(f"\n  [{i+1}] {icon} query='{query}' | {status}")
        print(f"      结果数: {result_count} (要求 >= {min_results})")
        if keywords:
            print(f"      关键词命中: {keyword_hits}/{len(keywords)} ({keywords})")
        print(f"      分数: [{scores_str}]")

        if passed:
            recall_hits += 1

    # ============================================================
    # 汇总
    # ============================================================
    print("\n" + "=" * 60)
    print("  评测汇总")
    print("=" * 60)

    recall_rate = recall_hits / total_queries * 100 if total_queries > 0 else 0
    print(f"\n  召回率 (Recall): {recall_hits}/{total_queries} = {recall_rate:.0f}%")

    if recall_rate >= 80:
        print(f"  结论: 🟢 良好，召回率达标")
    elif recall_rate >= 60:
        print(f"  结论: 🟡 一般，建议优化 chunk_size 或换 Embedding 模型")
    else:
        print(f"  结论: 🔴 差，需要系统性排查")

    # 清理
    print(f"\n[清理] 清空知识库...")
    api_get("/api/local_kb/clear")

    print("\n" + "=" * 60)
    print("  评测完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
