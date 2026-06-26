"""
TTS Service - edge-tts wrapper
Uses Microsoft Edge TTS (free, excellent Chinese quality)
"""
import asyncio
import os
import uuid
import json
import time
import edge_tts
from pathlib import Path

TTS_CACHE_DIR = Path(__file__).parent.parent / "tts_cache"

# Available Chinese voices
VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女声，温暖)", "gender": "female", "styles": ["cheerful", "sad", "angry", "fear", "disgusted", "serious", "affectionate", "gentle", "lyrical"]},
    {"id": "zh-CN-YunxiNeural", "name": "云希 (男声，新闻)", "gender": "male", "styles": ["cheerful", "sad", "angry", "fear", "disgusted", "serious", "embarrassed", "narration-professional"]},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓伊 (女声，活泼)", "gender": "female", "styles": ["cheerful", "sad", "angry", "fear", "disgusted", "serious"]},
    {"id": "zh-CN-YunjianNeural", "name": "云健 (男声，运动)", "gender": "male", "styles": ["cheerful", "sad", "angry", "fear", "disgusted", "serious", "sports", "narration-sports"]},
    {"id": "zh-CN-YunyangNeural", "name": "云扬 (男声，新闻)", "gender": "male", "styles": ["cheerful", "sad", "angry", "fear", "disgusted", "serious", "narration-professional"]},
]


def get_voices() -> list:
    """Return list of Chinese voices"""
    return VOICES


async def _synthesize_to_file(text: str, voice: str, rate: str, pitch: str,
                              output_path: str) -> list[dict]:
    """Internal: synthesize speech to a file, return real WordBoundary timestamps"""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    word_timestamps = []
    current_time = 0

    # Stream to capture WordBoundary events for precise timestamps
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                offset = chunk.get("offset", 0)
                duration = chunk.get("duration", 0)
                word_text = chunk.get("text", "")
                # Convert from 100-nanosecond units to milliseconds
                start_ms = offset / 10000
                dur_ms = duration / 10000
                word_timestamps.append({
                    "word": word_text,
                    "start_ms": round(start_ms),
                    "end_ms": round(start_ms + dur_ms),
                })
                current_time = start_ms + dur_ms

    return word_timestamps


async def synthesize(text: str, voice: str = "zh-CN-XiaoxiaoNeural",
                     rate: str = "+0%", pitch: str = "+0Hz") -> dict:
    """
    Synthesize text to speech, cache the result.
    Returns dict with audio_url and approximate word timestamps.
    """
    os.makedirs(TTS_CACHE_DIR, exist_ok=True)

    # Generate cache key
    import hashlib
    cache_key = hashlib.md5(f"{text}|{voice}|{rate}|{pitch}".encode()).hexdigest()
    audio_filename = f"{cache_key}.mp3"
    audio_path = TTS_CACHE_DIR / audio_filename
    ts_filename = f"{cache_key}.json"
    ts_path = TTS_CACHE_DIR / ts_filename

    # Return cached if exists
    if not audio_path.exists():
        word_ts = await _synthesize_to_file(text, voice, rate, pitch, str(audio_path))
        # Cache timestamps (use real WordBoundary data when available)
        if word_ts:
            timestamps = word_ts
            with open(ts_path, "w", encoding="utf-8") as f:
                json.dump(timestamps, f, ensure_ascii=False)
        else:
            timestamps = _generate_timestamps(text, audio_path)
            with open(ts_path, "w", encoding="utf-8") as f:
                json.dump(timestamps, f, ensure_ascii=False)
    elif ts_path.exists():
        with open(ts_path, "r", encoding="utf-8") as f:
            timestamps = json.load(f)
    else:
        timestamps = _generate_timestamps(text, audio_path)

    # Calculate actual duration from MP3 metadata (mutagen is more accurate)
    if timestamps and timestamps[-1].get("end_ms", 0) > 0:
        duration_ms = timestamps[-1]["end_ms"]
    else:
        duration_ms = _get_mp3_duration_ms(audio_path)

    return {
        "audio_url": f"/api/tts/audio/{audio_filename}",
        "duration_ms": duration_ms,
        "word_timestamps": timestamps,
    }


def _get_mp3_duration_ms(audio_path: Path) -> int:
    """使用 mutagen 读取实际 MP3 时长（毫秒）"""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(str(audio_path))
        if audio.info.length > 0:
            return int(audio.info.length * 1000)
    except Exception:
        pass
    # Fallback: rough estimate from file size
    file_size = audio_path.stat().st_size
    return int(file_size / 16)


def _generate_timestamps(text: str, audio_path: Path) -> list:
    """Generate approximate word timestamps by distributing text evenly over audio duration"""
    total_duration_ms = _get_mp3_duration_ms(audio_path)

    # Split text into segments (by punctuation or characters)
    import re
    segments = []
    # Split by Chinese punctuation boundaries
    parts = re.split(r'([，。！？、,\.\!\?\s])', text)
    current = ""
    for p in parts:
        if not p:
            continue
        if re.match(r'[，。！？、,\.\!\?\s]', p):
            if current:
                segments.append(current + p)
                current = ""
        else:
            current += p
    if current:
        segments.append(current)

    if not segments:
        segments = [text]

    # Distribute time evenly
    ms_per_char = total_duration_ms / max(len(text), 1)
    timestamps = []
    elapsed = 0

    for seg in segments:
        seg_duration = len(seg) * ms_per_char
        timestamps.append({
            "word": seg.strip(),
            "start_ms": int(elapsed),
            "end_ms": int(elapsed + seg_duration),
        })
        elapsed += seg_duration

    return timestamps


def get_audio_file(filename: str) -> Path | None:
    """Get path to a cached audio file"""
    audio_path = TTS_CACHE_DIR / filename
    if audio_path.exists():
        return audio_path
    return None
