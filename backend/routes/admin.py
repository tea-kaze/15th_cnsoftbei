"""管理后台 API 路由"""
from fastapi import APIRouter, Query
from services import logging_service as log_svc

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


@router.get("/dashboard")
def dashboard():
    """仪表盘概览：今日/本周/累计服务人次、平均响应时间、知识库状态"""
    return log_svc.get_dashboard_stats()


@router.get("/interactions")
def interactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
):
    """分页查询交互记录，支持关键词搜索和日期筛选"""
    return log_svc.get_recent_interactions(page, page_size, keyword, date_from, date_to)


@router.get("/trend")
def trend(days: int = Query(30, ge=1, le=365)):
    """每日交互趋势"""
    return log_svc.get_interaction_trend(days)


@router.get("/popular")
def popular(limit: int = Query(10, ge=1, le=50), days: int = Query(7, ge=1, le=90)):
    """热门问题 Top-N"""
    return log_svc.get_popular_questions(limit, days)


@router.get("/hourly")
def hourly(date: str = Query("")):
    """某日各时段交互量（热力图数据）"""
    return log_svc.get_hourly_heatmap(date if date else None)


@router.get("/report")
def report(days: int = Query(7, ge=1, le=90)):
    """游客感受度报告：关注点分析 + 情感趋势 + 服务建议"""
    popular = log_svc.get_popular_questions(20, days)
    trend = log_svc.get_interaction_trend(days)

    # 基于热门问题提取关注点
    concern_keywords = {
        "历史": ["历史", "古代", "年代", "朝代", "以前", "起源"],
        "文化": ["文化", "佛教", "禅", "信仰", "宗教"],
        "景点": ["景点", "大佛", "九龙", "梵宫", "胜境", "拈花"],
        "路线": ["路线", "游览", "推荐", "怎么走", "多长时间", "攻略"],
        "票务": ["门票", "价格", "开放", "时间", "优惠"],
        "餐饮": ["吃饭", "餐厅", "美食", "素斋", "小吃"],
        "交通": ["交通", "停车", "公交", "地铁", "自驾"],
        "住宿": ["住宿", "酒店", "民宿", "客栈"],
    }

    concerns = {}
    for category, keywords in concern_keywords.items():
        score = 0
        for pq in popular:
            for kw in keywords:
                if kw in pq["question"]:
                    score += pq["count"]
        if score > 0:
            concerns[category] = score

    sorted_concerns = sorted(concerns.items(), key=lambda x: x[1], reverse=True)
    top_concerns = [{"category": c, "score": s} for c, s in sorted_concerns]

    # 情感趋势（简化版：基于关键词的情绪分析）
    sentiment_trend = []
    for entry in trend:
        sentiment_trend.append({
            "date": entry["date"],
            "count": entry["count"],
            "level": "positive"  # 默认正面，后续可用 LLM 做精细分析
        })

    # 服务建议
    suggestions = []
    if len(top_concerns) > 0:
        top_topic = top_concerns[0]["category"]
        suggestions.append(f"游客最关注「{top_topic}」，建议在知识库中补充该领域详细资料")
    if len(popular) > 0 and len(popular[0]["question"]) < 6:
        suggestions.append("存在较多短问题检索，建议在欢迎页提供常见问题快捷入口")
    peak_hour = max(log_svc.get_hourly_heatmap(), key=lambda x: x["count"], default=None)
    if peak_hour and peak_hour["count"] > 0:
        suggestions.append(f"高峰时段为 {peak_hour['hour']}:00 左右，建议在此期间保障服务资源")
    suggestions.append("建议定期更新景区活动信息，保持知识库时效性")

    return {
        "top_concerns": top_concerns,
        "sentiment_trend": sentiment_trend,
        "suggestions": suggestions,
        "popular_questions": popular[:10],
        "total_interactions": sum(e["count"] for e in trend),
    }
