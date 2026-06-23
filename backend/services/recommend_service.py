"""个性化推荐服务 — 根据兴趣匹配游览路线"""
from services.rag import search

# 三条路线定义（从知识库提取）
ROUTES = {
    "history": {
        "id": "history",
        "name": "历史文化深度路线",
        "duration": "约6小时",
        "type": "深度游",
        "icon": "🏛️",
        "description": "适合对佛教文化、历史遗迹有浓厚兴趣的游客，深度探索灵山千年佛教文化底蕴。",
        "spots": [
            {"name": "灵山大照壁", "highlight": "全长39.8米，大型浮雕展现佛教文化博大精深"},
            {"name": "五智门", "highlight": "象征佛教五种智慧，庄严宏伟的门楼"},
            {"name": "胜境广场", "highlight": "灵山胜境核心集散区"},
            {"name": "降魔浮雕", "highlight": "展现释迦牟尼成道降魔的壮丽故事"},
            {"name": "天下第一掌", "highlight": "高11.7米，宽5.5米，象征'施无畏印'"},
            {"name": "慈恩塔", "highlight": "千年古刹遗址，感受历史变迁"},
            {"name": "佛坛广场", "highlight": "大型佛教法会举办地"},
            {"name": "灵山大佛", "highlight": "通高88米，世界最高露天青铜释迦牟尼立像"},
            {"name": "灵山梵宫", "highlight": "佛教艺术殿堂，穹顶壁画与《吉祥颂》演出"},
            {"name": "九龙灌浴", "highlight": "大型动态音乐群雕，再现佛祖诞生场景"},
            {"name": "五印坛城", "highlight": "藏传佛教文化瑰宝，转经筒祈福"},
            {"name": "佛足圣迹", "highlight": "佛教历史文化展览"},
        ],
        "tips": ["建议上午9点前入园避开高峰", "梵宫《吉祥颂》演出时间：10:35/11:30/14:00/16:00", "九龙灌浴每天4-5场表演，建议提前占位", "穿舒适的平底鞋，全程步行约6小时"],
    },
    "nature": {
        "id": "nature",
        "name": "自然风光爱好者路线",
        "duration": "约5小时",
        "type": "全景游",
        "icon": "🏞️",
        "description": "适合喜爱自然景观、摄影打卡的游客，登高望远饱览太湖美景。",
        "spots": [
            {"name": "景区入口", "highlight": "从入口乘坐观光车至佛坛"},
            {"name": "佛坛", "highlight": "庄严开阔，感受佛教圣地氛围"},
            {"name": "九龙灌浴", "highlight": "动态音乐群雕表演，水幕光影交织"},
            {"name": "登高观景台", "highlight": "远眺太湖全景，夕阳西下时'落霞与孤鹜齐飞'"},
            {"name": "灵山大佛", "highlight": "登216级台阶，俯瞰太湖与灵山半岛的绝佳视角"},
            {"name": "园林景观区", "highlight": "竹林、樱花、银杏，四季皆有不同景色"},
            {"name": "灵山精舍", "highlight": "禅意园林茶歇，品味素食斋饭（50元/位）"},
            {"name": "梵宫广场", "highlight": "傍晚时分，金色梵宫倒映水面，摄影绝佳"},
        ],
        "tips": ["推荐春秋季（3-5月、9-11月）游览，气候宜人", "傍晚登大佛观景台，可赏太湖日落", "灵山精舍品茶小憩，体验'无味一味'禅意生活", "带上相机，梵宫广场傍晚光影最佳"],
    },
    "family": {
        "id": "family",
        "name": "亲子家庭欢乐路线",
        "duration": "约4小时",
        "type": "轻松游",
        "icon": "👨‍👩‍👧‍👦",
        "description": "适合带老人小孩的家庭游客，节奏轻松，寓教于乐。",
        "spots": [
            {"name": "景区入口", "highlight": "轻松入园，可选观光车代步"},
            {"name": "九龙灌浴", "highlight": "动态表演让孩子直观感受佛祖诞生故事"},
            {"name": "降魔浮雕", "highlight": "讲述释迦牟尼成道故事，寓教于乐"},
            {"name": "天下第一掌", "highlight": "摸摸佛手，寓意吉祥平安，老少皆宜"},
            {"name": "百子戏弥勒", "highlight": "百个童子围绕弥勒，童趣盎然，孩子最爱"},
            {"name": "梵宫", "highlight": "色彩斑斓的壁画和《吉祥颂》演出，视觉盛宴"},
            {"name": "五印坛城", "highlight": "转经筒互动体验，了解藏族文化"},
        ],
        "tips": ["建议乘坐观光车减少步行", "景区提供素斋套餐35元/位，清淡适合孩子口味", "九龙灌浴前广场适合家庭合影", "梵宫内设休息区，可随时休息"],
    },
}


def classify_interest(user_input: str) -> str:
    """基于用户输入的关键词匹配路线类型"""
    text = user_input.lower()

    history_kw = ["历史", "文化", "佛教", "古迹", "古代", "千年", "传统", "深度", "禅", "宗教", "艺术"]
    nature_kw = ["自然", "风景", "风光", "山水", "太湖", "拍照", "摄影", "园林", "日落", "夕阳", "花", "全景"]
    family_kw = ["亲子", "孩子", "家庭", "老人", "小孩", "轻松", "休闲", "寓教于乐", "简单", "舒服"]

    scores = {"history": 0, "nature": 0, "family": 0}
    for kw in history_kw:
        if kw in text:
            scores["history"] += 1
    for kw in nature_kw:
        if kw in text:
            scores["nature"] += 1
    for kw in family_kw:
        if kw in text:
            scores["family"] += 1

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "history"  # 默认推荐历史文化路线
    return best


def get_recommendation(user_input: str) -> dict:
    """根据用户输入返回推荐路线"""
    route_key = classify_interest(user_input)
    route = ROUTES[route_key].copy()

    # 用 RAG 搜索补充相关知识
    related_chunks = search(user_input, top_k=3)
    route["knowledge_tips"] = related_chunks[:2] if related_chunks else []

    # 推荐理由
    reasons = {
        "history": "您对历史文化感兴趣，这条路线将带您深度探索灵山1300年的佛教传承",
        "nature": "您喜爱自然风光，这条路线专为摄影和观景设计，饱览太湖山水之美",
        "family": "您是和家人一起出游，这条轻松路线兼顾老人孩子的节奏，寓教于乐",
    }
    route["reason"] = reasons.get(route_key, "")

    return route
