"""景区旅游行为数据分析服务 — 基于 xlsx 数据增强管理后台报告"""
import os
import json
from collections import Counter
from datetime import datetime


def _get_xlsx_path() -> str:
    """获取 xlsx 数据文件路径"""
    return os.path.join(
        os.path.dirname(__file__), "..", "..",
        "示范景区公开资料包", "景点景区旅游数据行为分析数据.xlsx"
    )


def _get_cache_path() -> str:
    """获取缓存 JSON 路径"""
    return os.path.join(os.path.dirname(__file__), "..", "analytics_cache.json")


def load_xlsx_data(force_reload: bool = False) -> list[dict]:
    """加载灵山胜境的旅游行为数据（优先使用缓存）"""
    cache_path = _get_cache_path()

    # 优先使用缓存
    if not force_reload and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # 从 xlsx 读取
    xlsx_path = _get_xlsx_path()
    if not os.path.exists(xlsx_path):
        return []

    try:
        import openpyxl
        wb = openpyxl.load_workbook(xlsx_path, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        wb.close()

        records = []
        for row in rows:
            if not row[4] or "灵山" not in str(row[4]):
                continue
            records.append({
                "tourist_id": str(row[0]) if row[0] else "",
                "age": int(row[2]) if row[2] else 0,
                "gender": str(row[3]) if row[3] else "",
                "visit_date": str(row[7])[:10] if row[7] else "",
                "stay_duration": float(row[8]) if row[8] else 0,
                "ticket_cost": float(row[9]) if row[9] else 0,
                "food_cost": float(row[10]) if row[10] else 0,
                "shopping_cost": float(row[11]) if row[11] else 0,
                "transport_cost": float(row[12]) if row[12] else 0,
                "entertainment_cost": float(row[13]) if row[13] else 0,
                "total_cost": float(row[14]) if row[14] else 0,
                "group_size": int(row[15]) if row[15] else 1,
                "satisfaction": str(row[16]) if row[16] else "",
            })

        # 写入缓存
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False)
        except IOError:
            pass

        return records
    except ImportError:
        return []


def get_analytics_summary() -> dict:
    """获取游客行为分析摘要（用于数据大屏和报告）"""
    records = load_xlsx_data()
    if not records:
        return {"available": False}

    total = len(records)

    # 年龄分布
    age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-60": 0, "60+": 0}
    for r in records:
        a = r["age"]
        if a <= 25:
            age_groups["18-25"] += 1
        elif a <= 35:
            age_groups["26-35"] += 1
        elif a <= 45:
            age_groups["36-45"] += 1
        elif a <= 60:
            age_groups["46-60"] += 1
        else:
            age_groups["60+"] += 1

    # 性别分布
    gender_count = Counter(r["gender"] for r in records if r["gender"])

    # 月度访问趋势
    monthly = Counter()
    for r in records:
        if r["visit_date"]:
            monthly[r["visit_date"][:7]] += 1
    monthly_trend = [{"month": k, "count": v} for k, v in sorted(monthly.items())]

    # 平均停留时长
    avg_stay = sum(r["stay_duration"] for r in records) / total if total else 0

    # 消费分析
    avg_ticket = sum(r["ticket_cost"] for r in records) / total if total else 0
    avg_food = sum(r["food_cost"] for r in records) / total if total else 0
    avg_shopping = sum(r["shopping_cost"] for r in records) / total if total else 0
    avg_transport = sum(r["transport_cost"] for r in records) / total if total else 0
    avg_entertainment = sum(r["entertainment_cost"] for r in records) / total if total else 0
    avg_total = sum(r["total_cost"] for r in records) / total if total else 0

    # 满意度分布
    satisfaction_count = Counter(r["satisfaction"] for r in records if r["satisfaction"])

    # 团队规模分析
    group_analysis = {"solo": 0, "small(2-3)": 0, "medium(4-6)": 0, "large(7+)": 0}
    for r in records:
        gs = r["group_size"]
        if gs <= 1:
            group_analysis["solo"] += 1
        elif gs <= 3:
            group_analysis["small(2-3)"] += 1
        elif gs <= 6:
            group_analysis["medium(4-6)"] += 1
        else:
            group_analysis["large(7+)"] += 1

    # 高峰时段（基于停留时长推断）
    peak_months = monthly.most_common(3)

    return {
        "available": True,
        "total_records": total,
        "data_source": "景区旅游行为分析数据（xlsx）",
        "age_distribution": age_groups,
        "gender_distribution": dict(gender_count),
        "monthly_trend": monthly_trend,
        "avg_stay_hours": round(avg_stay, 1),
        "avg_costs": {
            "ticket": round(avg_ticket, 0),
            "food": round(avg_food, 0),
            "shopping": round(avg_shopping, 0),
            "transport": round(avg_transport, 0),
            "entertainment": round(avg_entertainment, 0),
            "total": round(avg_total, 0),
        },
        "satisfaction_distribution": dict(satisfaction_count),
        "group_size_distribution": group_analysis,
        "peak_months": [{"month": m, "count": c} for m, c in peak_months],
    }
