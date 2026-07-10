#!/usr/bin/env python3
"""M1+M2+M3: 语音识别全链路优化 — 集成测试（直接函数调用 + API）"""
import sys
sys.path.insert(0, "backend")

from app.services.question_judge import (
    correct_terms, post_process_transcript,
    is_interview_question, validate_question,
    TERM_CORRECTIONS,
)
import requests
import json

BASE_URL = "http://localhost:8001/api"
passed = 0
failed = 0

def log_pass(msg):
    global passed
    passed += 1
    print(f"  ✅ PASS: {msg}")

def log_fail(msg, detail=""):
    global failed
    failed += 1
    print(f"  ❌ FAIL: {msg}")
    if detail:
        print(f"     {detail}")

# ═══════════════════════════════════════════════════════════
# M2: correct_terms() 单元测试（绕过 API 去重）
# ═══════════════════════════════════════════════════════════
def test_m2_correct_terms_unit():
    print("\n📝 M2 correct_terms() 单元测试")
    print("-" * 50)

    cases = [
        ("你用过k 8 s吗", "你用过Kubernetes吗", True, "K8s 空格分隔"),
        ("什么是k8 s", "什么是Kubernetes", True, "k8s 混合"),
        ("c i c d流水线", "CI/CD流水线", True, "CI/CD"),
        ("会抓娃吗", "会Java吗", True, "Java 音译"),
        ("威武服务架构", "微服务架构", True, "微服务 音译"),
        ("g r p c和rest的区别", "gRPC和rest的区别", True, "gRPC（rest 太常见不纳入词库）"),
        ("容器话和虚拟机", "容器化和虚拟机", True, "容器化"),
        ("解释一下热格", "解释一下RAG", True, "RAG 音译"),
        ("够语言的并发模型", "Go语言的并发模型", True, "Go语言"),
        ("卡夫卡消息队列", "Kafka消息队列", True, "Kafka"),
        ("道客和虚拟机", "Docker和虚拟机", True, "Docker 道客"),
        ("刀客容器", "Docker容器", True, "Docker 刀客"),
        ("芒狗 db怎么用", "MongoDB怎么用", True, "MongoDB"),
        ("post grace和mysql", "PostgreSQL和MySQL", True, "PostgreSQL"),
        ("耐克斯反向代理", "Nginx反向代理", True, "Nginx"),
        ("store 法则怎么用", "STAR法则怎么用", True, "STAR法则"),
        ("type script怎么类型推导", "TypeScript怎么类型推导", True, "TypeScript"),
    ]

    for raw, expected, should_correct, desc in cases:
        result, was_corrected = correct_terms(raw)
        if result == expected and was_corrected == should_correct:
            log_pass(desc)
        else:
            log_fail(desc, f"期望: '{expected}' (corrected={should_correct}), 实际: '{result}' (corrected={was_corrected})")

# M2: 双重替换防护
def test_m2_no_double_replace():
    print("\n📝 M2 双重替换防护（子串匹配）")
    print("-" * 50)

    # k8s → Kubernetes 后不应出现 KubernetElasticsearch
    result, _ = correct_terms("k 8 s 集群")
    assert "KubernetElasticsearch" not in result, f"意外双替换: {result}"
    log_pass("k 8 s 未双替换为 KubernetElasticsearch")

    # 威武服务 → 微服务后不应出现 微服务务
    result, _ = correct_terms("威武服务")
    assert "微服务务" not in result, f"意外双替换: {result}"
    log_pass("威武服务 未双替换为 微服务务")

    # ASCII 边界：中文里嵌入 e s 不应被替换
    result, _ = correct_terms("test测试")
    # "test" 不含需要纠正的词条，应不变
    assert result == "test测试", f"意外替换: {result}"
    log_pass("纯英文 test 未被错误替换")

# M2: post_process_transcript 管线
def test_m2_post_process():
    print("\n📝 M2 post_process_transcript() 管线")
    print("-" * 50)

    result = post_process_transcript("  你用过k 8 s吗  ", 0.85)
    assert result["corrected"] == "你用过Kubernetes吗"
    assert result["was_corrected"] is True
    assert result["confidence"] == 0.85
    assert result["low_confidence"] is False
    log_pass("高置信度 + 术语纠错: 管线正确")

    result = post_process_transcript("什么是react", 0.45)
    assert result["corrected"] == "什么是React"
    assert result["was_corrected"] is True
    assert result["low_confidence"] is True
    log_pass("低置信度标记: 管线正确")

    result = post_process_transcript("正常文本", 0.9)
    assert result["corrected"] == "正常文本"
    assert result["was_corrected"] is False
    log_pass("无需纠错: 管线正确")

# ═══════════════════════════════════════════════════════════
# M3: is_interview_question() 单元测试
# ═══════════════════════════════════════════════════════════
def test_m3_interview_detect():
    print("\n📝 M3 is_interview_question() 单元测试")
    print("-" * 50)

    # 应通过的面试问题
    pass_cases = [
        "什么是微服务架构",
        "怎么优化数据库性能",
        "请介绍一下你的项目",
        "如何实现分布式锁",
        "react和vue的区别",
        "你能说说设计模式吗",
        "谈谈你对高可用的理解",
        "举例说明你在项目中遇到的挑战",
        "做过哪些性能优化",
        "描述一下你熟悉的算法",
    ]
    for q in pass_cases:
        ok, reason = is_interview_question(q)
        if ok:
            log_pass(f"通过: '{q[:25]}...'")
        else:
            log_fail(f"应通过但拒绝: '{q[:25]}...' (reason: {reason})")

    # 应过滤的非面试文本
    reject_cases = [
        ("好的", "确认类"),
        ("嗯", "确认类"),
        ("对", "确认类"),
        ("是的", "确认类"),
        ("可以", "确认类"),
        ("行", "确认类"),
        ("没问题", "确认类"),
        ("好", "确认类"),
        ("ok", "确认类"),
        ("OK", "确认类"),
        ("ab", "过短"),
        ("abc", "过短"),
    ]
    for text, category in reject_cases:
        ok, reason = is_interview_question(text)
        if not ok:
            log_pass(f"{category}过滤: '{text}'")
        else:
            log_fail(f"{category}应过滤但通过: '{text}'")

# M3: validate_question 完整链路
def test_m3_validate_question():
    print("\n📝 M3 validate_question() 端到端（含 M2+M3）")
    print("-" * 50)

    # 正常面试问题 + 术语纠错
    result = validate_question("请介绍一下k 8 s", 0.9)
    assert result["is_valid"] is True
    assert result["corrected_text"] == "请介绍一下Kubernetes"
    assert result["was_corrected"] is True
    log_pass("有效问题 + 术语纠错: is_valid=True, corrected=Kubernetes")

    # 确认类文本过滤（好的=2字符，先被长度检查拦截）
    result = validate_question("好的", 0.9)
    assert result["is_valid"] is False
    log_pass(f"确认类过滤: is_valid=False, reason={result['reason']}")
    
    # 确认类四字以上应被意图识别过滤
    result = validate_question("没问题啊", 0.9)
    assert result["is_valid"] is False
    assert "意图过滤" in result["reason"]
    log_pass(f"意图过滤: is_valid=False, reason={result['reason']}")

    # 空文本
    result = validate_question("", 1.0)
    assert result["is_valid"] is False
    assert result["reason"] == "空文本"
    log_pass("空文本过滤")

    # None 文本
    result = validate_question(None, 1.0)
    assert result["is_valid"] is False
    log_pass("None 文本过滤")

    # 短文本
    result = validate_question("ab", 1.0)
    assert result["is_valid"] is False
    log_pass("过短文本过滤")

    # 低置信度（不拒绝但标记）
    result = validate_question("什么是设计模式", 0.4)
    assert result["is_valid"] is True
    assert result.get("low_confidence") is True
    log_pass("低置信度标记: is_valid=True, low_confidence=True")

# ═══════════════════════════════════════════════════════════
# API 集成测试（绕过内存去重 — 每次用不同文本）
# ═══════════════════════════════════════════════════════════
def test_api_integration():
    print("\n📝 API /transcript 集成测试（含 M2+M3）")
    print("-" * 50)

    # 清空数据库
    requests.delete(f"{BASE_URL}/dialogues")

    # 测试1: 正常提交
    res = requests.post(f"{BASE_URL}/transcript", json={
        "text": "请介绍一下react的状态管理", "confidence": 0.92
    })
    data = res.json()
    if data["data"]["is_valid"] is True:
        log_pass("正常面试问题提交成功")
    else:
        log_fail("正常面试问题提交失败", json.dumps(data, ensure_ascii=False))

    # 测试2: 确认类过滤
    res = requests.post(f"{BASE_URL}/transcript", json={
        "text": "好的", "confidence": 0.9
    })
    data = res.json()
    if data["data"]["is_valid"] is False:
        log_pass(f"确认类过滤通过 API: reason={data['data']['reason']}")
    else:
        log_fail("确认类应被 API 过滤", json.dumps(data, ensure_ascii=False))

    # 测试3: 术语纠错 — question 字段包含修正文本
    res = requests.post(f"{BASE_URL}/transcript", json={
        "text": "请讲讲a p i的设计", "confidence": 0.88
    })
    data = res.json()
    question_text = data.get("data", {}).get("question", "")
    if "API" in question_text and "a p i" not in question_text:
        log_pass("API 术语纠错生效: question 包含修正后文本")
    else:
        log_fail("术语纠错未生效", f"question='{question_text}'")

    # 测试4: confidence 传递
    res = requests.post(f"{BASE_URL}/transcript", json={
        "text": "说说你对分布式系统的理解", "confidence": 0.72
    })
    data = res.json()
    if data["data"]["is_valid"] is True:
        log_pass("confidence=0.72 正确传递并处理")
    else:
        log_fail("confidence 传递失败", json.dumps(data, ensure_ascii=False))

# ═══════════════════════════════════════════════════════════
# M1 前端构建验证
# ═══════════════════════════════════════════════════════════
def test_m1_frontend_build():
    print("\n📝 M1 前端构建验证")
    print("-" * 50)

    import subprocess
    import os

    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if not os.path.isdir(frontend_dir):
        log_fail("frontend 目录不存在")
        return

    # type-check
    result = subprocess.run(
        ["npx", "vue-tsc", "--noEmit"],
        cwd=frontend_dir, capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        log_pass("vue-tsc 类型检查通过")
    else:
        log_fail("vue-tsc 类型检查失败", result.stderr[:300])

    # build
    result = subprocess.run(
        ["npx", "vite", "build"],
        cwd=frontend_dir, capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        log_pass("vite build 构建成功")
    else:
        log_fail("vite build 构建失败", result.stderr[:300])

# ═══════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("🎯 M1+M2+M3 语音识别全链路优化 — 集成测试")
    print("=" * 60)

    # M2 单元测试
    test_m2_correct_terms_unit()
    test_m2_no_double_replace()
    test_m2_post_process()

    # M3 单元测试
    test_m3_interview_detect()
    test_m3_validate_question()

    # API 集成测试
    test_api_integration()

    # M1 前端构建
    test_m1_frontend_build()

    print("\n" + "=" * 60)
    total = passed + failed
    pct = (passed / total * 100) if total > 0 else 0
    print(f"📊 测试结果: {passed} 通过, {failed} 失败 ({pct:.1f}%)")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
