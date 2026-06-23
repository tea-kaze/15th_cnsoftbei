"""VTube Studio 数字人控制 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from services.vts_service import get_vts

router = APIRouter(prefix="/api/vts", tags=["数字人"])


class TTSResult(BaseModel):
    """TTS 合成结果，用于驱动口型同步"""
    text: str
    audio_url: str = ""
    duration_ms: int = 0
    word_timestamps: list = []


class EmotionRequest(BaseModel):
    emotion: str  # happy, sad, surprised, angry, neutral
    active: bool = True


@router.get("/status")
def status():
    """获取 VTube Studio 连接状态"""
    vts = get_vts()
    return vts.get_stats()


@router.post("/connect")
def connect():
    """手动连接 VTube Studio"""
    vts = get_vts()
    ok = vts.connect()
    return {"connected": ok, "message": "已连接" if ok else "连接失败，请确认 VTube Studio 已启动并开启 API"}


@router.post("/expression")
def set_expression(req: EmotionRequest):
    """设置数字人表情"""
    vts = get_vts()
    # neutral = 停用所有表情
    if req.emotion == "neutral":
        for exp in vts.expressions:
            vts.set_expression(exp, False)
        return {"ok": True, "emotion": "neutral"}

    ok = vts.set_expression(req.emotion, req.active)
    return {"ok": ok, "emotion": req.emotion}


@router.post("/speak")
def speak(tts: TTSResult):
    """触发数字人口型同步（传入 TTS 结果）"""
    vts = get_vts()
    vts.start_mouth_sync(tts.word_timestamps, tts.duration_ms)
    return {"ok": True, "duration_ms": tts.duration_ms}


@router.post("/stop")
def stop_speak():
    """停止口型同步"""
    vts = get_vts()
    vts.stop_mouth_sync()
    return {"ok": True}


@router.post("/hotkey")
def trigger_hotkey(data: dict):
    """触发热键动作（挥手、鞠躬等）"""
    vts = get_vts()
    hotkey_id = data.get("hotkey_id", "")
    if not hotkey_id:
        return {"ok": False, "error": "hotkey_id 不能为空"}
    ok = vts.trigger_hotkey(hotkey_id)
    return {"ok": ok}


@router.post("/move")
def move_model(data: dict):
    """移动/旋转/缩放模型"""
    vts = get_vts()
    vts.move_model(
        x=data.get("x", 0),
        y=data.get("y", 0),
        rotation=data.get("rotation", 0),
        size=data.get("size", 1.0),
        time_sec=data.get("time_sec", 0.5),
    )
    return {"ok": True}


@router.post("/greet")
def greet():
    """欢迎流程：挥手 + 微笑"""
    vts = get_vts()
    # 挥手
    vts.trigger_hotkey("wave") if vts.connected else None
    # 微笑
    vts.set_expression("happy", True if vts.connected else None)
    return {"ok": True}
