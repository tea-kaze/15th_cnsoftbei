"""个性化推荐 API 路由"""
from fastapi import APIRouter
from services.recommend_service import get_recommendation, ROUTES

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


@router.post("")
def recommend(data: dict):
    """根据用户兴趣推荐游览路线"""
    user_input = data.get("interest", "") or data.get("message", "") or ""
    if not user_input.strip():
        # 默认返回所有路线供选择
        return {"routes": list(ROUTES.values()), "recommended": None}

    result = get_recommendation(user_input.strip())
    return {"routes": list(ROUTES.values()), "recommended": result}
