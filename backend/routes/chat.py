import time
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 情绪关键词映射
EMOTION_MAP = [
    ("surprised", ["惊人", "震撼", "高达", "最大", "第一", "奇迹", "88米", "世界之最"]),
    ("happy", ["欢迎", "开心", "高兴", "推荐", "美好", "精彩", "值得", "壮丽", "美丽", "著名"]),
    ("sad", ["抱歉", "遗憾", "可惜", "难过"]),
]


def detect_emotion(text: str) -> str:
    """从文本中检测情绪标签"""
    for emotion, keywords in EMOTION_MAP:
        for kw in keywords:
            if kw in text:
                return emotion
    return "neutral"


def _do_rag_and_log(question: str, answer: str, start_time: float,
                     request: Request, emotion: str = "neutral"):
    """记录交互日志"""
    try:
        from services.logging_service import log_interaction
        elapsed = int((time.time() - start_time) * 1000)
        ip = request.client.host if request.client else ""
        ua = request.headers.get("user-agent", "")
        log_interaction(question, answer, [], elapsed, ip, ua, emotion)
    except Exception:
        pass


def _trigger_vts(emotion: str):
    """触发 VTS 表情（非阻塞）"""
    if emotion == "neutral":
        return
    try:
        from services.vts_service import get_vts
        vts = get_vts()
        if vts.connected:
            vts.set_expression(emotion, True)
    except Exception:
        pass


@router.post("/ask")
async def ask(data: dict, request: Request):
    from services.rag import search

    question = data.get("question", "").strip()
    history = data.get("history", [])  # 多轮对话上下文
    if not question:
        return {"error": "问题不能为空"}

    start_time = time.time()
    chunks = search(question, top_k=5)

    try:
        from services.llm import answer_with_context
        answer = answer_with_context(question, chunks, history)
    except Exception as e:
        answer = f"[LLM未配置] 请先设置API Key。\n检索到的相关内容：\n\n" + "\n---\n".join(chunks) if chunks else "未找到相关内容"
        sources = [c[:80] + ("..." if len(c) > 80 else "") for c in chunks]
        _do_rag_and_log(question, answer, start_time, request)
        return {"answer": answer, "sources": sources, "error": str(e), "emotion": "neutral"}

    sources = [c[:80] + ("..." if len(c) > 80 else "") for c in chunks]
    emotion = detect_emotion(answer)

    _do_rag_and_log(question, answer, start_time, request, emotion)
    _trigger_vts(emotion)

    return {"answer": answer, "sources": sources, "emotion": emotion}


@router.post("/ask/stream")
async def ask_stream(data: dict, request: Request):
    """SSE 流式问答端点"""
    from services.rag import search

    question = data.get("question", "").strip()
    history = data.get("history", [])
    if not question:
        return StreamingResponse(
            iter([f"data: {json.dumps({'error': '问题不能为空'})}\n\n"]),
            media_type="text/event-stream",
        )

    chunks = search(question, top_k=5)

    from services.llm import answer_stream

    async def event_generator():
        full_answer = ""
        start_time = time.time()
        try:
            for token in answer_stream(question, chunks, history):
                full_answer += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # 流式结束后记录日志和触发 VTS
            emotion = detect_emotion(full_answer) if full_answer else "neutral"
            _do_rag_and_log(question, full_answer, start_time, request, emotion)
            _trigger_vts(emotion)
            # 发送结束信号（含完整答案和情绪）
            sources = [c[:80] + ("..." if len(c) > 80 else "") for c in chunks]
            yield f"data: {json.dumps({'done': True, 'emotion': emotion, 'sources': sources})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
