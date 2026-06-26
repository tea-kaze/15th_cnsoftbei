"""事实性问答准确率测试

基于知识库内容构建 50 道事实性问答题，通过 RAG + LLM 验证准确率。
运行方式: python tests/test_accuracy.py
"""

import sys
import os
import json
import time

# 添加 backend 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.rag import search
from services.llm import answer_with_context

# ============================================================
# 测试用例：50 道事实性问题（基于灵山胜境知识库）
# 每道题包含：question, expected_keywords（正确答案必须包含的关键词）
# ============================================================
TEST_CASES = [
    # ---- 景区概况 ----
    {"question": "灵山胜境位于哪个城市？", "keywords": ["无锡"]},
    {"question": "灵山胜境占地面积约多少？", "keywords": ["30万", "30万平方米"]},
    {"question": "灵山胜境是国家几A级景区？", "keywords": ["5A", "AAAAA"]},
    {"question": "灵山胜境的历史可以追溯到哪个朝代？", "keywords": ["唐代", "唐贞观", "玄奘"]},
    {"question": "小灵山这个名字是谁起的？", "keywords": ["玄奘"]},
    {"question": "灵山胜境被誉为哪两个称号？", "keywords": ["东方佛国", "太湖佛国"]},

    # ---- 灵山大佛 ----
    {"question": "灵山大佛有多高？", "keywords": ["88米", "88"]},
    {"question": "灵山大佛佛体高度是多少？", "keywords": ["79米", "79"]},
    {"question": "灵山大佛莲花瓣高度是多少？", "keywords": ["9米", "9"]},
    {"question": "灵山大佛含台基总高度是多少？", "keywords": ["101.5", "101"]},
    {"question": "灵山大佛总用铜量是多少吨？", "keywords": ["725"]},
    {"question": "灵山大佛是哪一年落成开光的？", "keywords": ["1997"]},
    {"question": "灵山大佛右手施什么印？", "keywords": ["无畏印", "施无畏"]},
    {"question": "灵山大佛左手施什么印？", "keywords": ["与愿印"]},
    {"question": "登大佛的台阶有多少级？", "keywords": ["216"]},
    {"question": "灵山大佛是什么材质的？", "keywords": ["青铜", "铜"]},

    # ---- 九龙灌浴 ----
    {"question": "九龙灌浴总高度是多少？", "keywords": ["27", "27.2", "27.5"]},
    {"question": "九龙灌浴中央太子佛像多高？", "keywords": ["7.2"]},
    {"question": "九龙灌浴太子佛重量是多少？", "keywords": ["12吨", "12"]},
    {"question": "九龙灌浴表演的是什么故事？", "keywords": ["诞生", "佛祖", "释迦牟尼"]},
    {"question": "九龙灌浴每天有几场表演？", "keywords": ["4", "5", "4-5"]},

    # ---- 灵山梵宫 ----
    {"question": "灵山梵宫建筑面积是多少？", "keywords": ["7.2万", "72000"]},
    {"question": "灵山梵宫造价多少？", "keywords": ["18亿", "18"]},
    {"question": "灵山梵宫顶部有几座莲花圣塔？", "keywords": ["五座", "5"]},
    {"question": "灵山梵宫穹顶用了多少黄金绘制？", "keywords": ["100公斤", "100"]},
    {"question": "灵山梵宫穹顶有多少尊飞天？", "keywords": ["148"]},
    {"question": "灵山梵宫《吉祥颂》演出每天几场？", "keywords": ["4"]},
    {"question": "灵山梵宫被誉为？", "keywords": ["卢浮宫", "东方卢浮"]},

    # ---- 祥符禅寺 ----
    {"question": "祥符禅寺始建于哪个朝代？", "keywords": ["唐代", "唐贞观"]},
    {"question": "祥符禅寺原名是什么？", "keywords": ["小灵山庵"]},
    {"question": "祥符禅寺的钟有多重？", "keywords": ["12.8吨", "12.8"]},
    {"question": "祥符禅寺内有什么古树？", "keywords": ["银杏"]},

    # ---- 五印坛城 ----
    {"question": "五印坛城是什么佛教文化的代表？", "keywords": ["藏传佛教", "藏传"]},
    {"question": "五印坛城占地面积约多少？", "keywords": ["5000"]},
    {"question": "五印坛城有多少个转经筒？", "keywords": ["108"]},
    {"question": "五印坛城四面环水的是什么？", "keywords": ["香水海"]},

    # ---- 天下第一掌 ----
    {"question": "天下第一掌有多高？", "keywords": ["11.7"]},
    {"question": "天下第一掌有多宽？", "keywords": ["5.5"]},

    # ---- 灵山大照壁 ----
    {"question": "灵山大照壁全长多少米？", "keywords": ["39.8"]},
    {"question": "灵山大照壁被誉为什么？", "keywords": ["华夏第一壁"]},

    # ---- 降魔浮雕 ----
    {"question": "降魔浮雕长多少米？", "keywords": ["26"]},
    {"question": "降魔浮雕高多少米？", "keywords": ["4.6"]},

    # ---- 阿育王柱 ----
    {"question": "阿育王柱通高多少米？", "keywords": ["16.9"]},
    {"question": "阿育王柱总重量多少吨？", "keywords": ["180"]},

    # ---- 五智门 ----
    {"question": "五智门有多高？", "keywords": ["16.8"]},
    {"question": "五智门六柱代表什么？", "keywords": ["六度", "波罗蜜"]},

    # ---- 门票/实用信息 ----
    {"question": "灵山胜境成人门票多少钱？", "keywords": ["210"]},
    {"question": "灵山胜境半价票多少钱？", "keywords": ["105"]},
    {"question": "灵山胜境观光车票价多少？", "keywords": ["40"]},
    {"question": "灵山胜境网购联票多少钱？", "keywords": ["225", "联票"]},
    {"question": "景区建议几点前入园避开高峰？", "keywords": ["9点", "9"]},
]


def evaluate_answer(question: str, answer: str, expected_keywords: list[str]) -> dict:
    """判断回答是否包含预期关键词"""
    answer_lower = answer.lower()
    matched = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    is_correct = len(matched) > 0
    return {
        "question": question,
        "answer_preview": answer[:120],
        "expected": expected_keywords,
        "matched": matched,
        "correct": is_correct,
    }


def run_tests() -> dict:
    """运行全部测试"""
    results = []
    total = len(TEST_CASES)
    correct = 0
    total_time = 0

    print(f"\n{'='*60}")
    print(f"  灵山胜境 AI 导游 —— 事实性问答准确率测试")
    print(f"  测试用例数: {total}")
    print(f"{'='*60}\n")

    for i, tc in enumerate(TEST_CASES):
        question = tc["question"]
        keywords = tc["keywords"]

        # RAG 检索相关知识（提高 top_k 以提升召回率）
        chunks = search(question, top_k=5)

        # LLM 生成回答
        start = time.time()
        answer = answer_with_context(question, chunks)
        elapsed = time.time() - start
        total_time += elapsed

        # 评估
        result = evaluate_answer(question, answer, keywords)
        result["index"] = i + 1
        result["elapsed"] = round(elapsed, 2)
        results.append(result)

        if result["correct"]:
            correct += 1
            icon = "✅"
        else:
            icon = "❌"

        print(f"  [{icon}] #{i+1:02d} {question}")
        print(f"       期望关键词: {keywords}")
        print(f"       匹配到: {result['matched'] if result['matched'] else '无'}")
        print(f"       回答片段: {result['answer_preview']}...")
        print(f"       耗时: {elapsed:.1f}s")
        print()

    accuracy = correct / total * 100 if total > 0 else 0
    avg_time = total_time / total if total > 0 else 0

    print(f"{'='*60}")
    print(f"  测试结果")
    print(f"  正确: {correct}/{total}")
    print(f"  准确率: {accuracy:.1f}%")
    print(f"  平均响应时间: {avg_time:.1f}s")
    print(f"  赛题要求: ≥ 90%")
    if accuracy >= 90:
        print(f"  ✅ 达标！准确率满足赛题要求")
    else:
        print(f"  ❌ 未达标，差距: {90 - accuracy:.1f}%")
    print(f"{'='*60}\n")

    # 列出答错的题目
    failed = [r for r in results if not r["correct"]]
    if failed:
        print("需改进的问题:")
        for r in failed:
            print(f"  - #{r['index']:02d} {r['question']}")
            print(f"    期望: {r['expected']}  回答: {r['answer_preview'][:80]}...")
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 1),
        "avg_response_time": round(avg_time, 1),
        "passed": accuracy >= 90,
        "results": results,
    }


if __name__ == "__main__":
    run_tests()
