"""TTS API Routes"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services import tts_service

router = APIRouter(prefix="/api/tts", tags=["TTS"])


class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    rate: Optional[str] = None
    pitch: Optional[str] = None


@router.get("/voices")
async def list_voices():
    """Get available TTS voices"""
    return {"voices": tts_service.get_voices()}


@router.post("/synthesize")
async def synthesize_speech(req: SynthesizeRequest):
    """Convert text to speech, return audio URL and word timestamps"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    if len(req.text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long (max 1000 chars)")

    result = await tts_service.synthesize(
        text=req.text,
        voice=req.voice or "zh-CN-XiaoxiaoNeural",
        rate=req.rate or "+0%",
        pitch=req.pitch or "+0Hz",
    )
    return result


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve cached audio file"""
    audio_path = tts_service.get_audio_file(filename)
    if audio_path is None:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(audio_path), media_type="audio/mpeg")
