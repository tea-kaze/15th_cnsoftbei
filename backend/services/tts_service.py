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


async def _synthesize_to_file(text: str, voice: str, rate: str, pitch: str, output_path: str):
    """Internal: synthesize speech to a file"""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)


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
        await _synthesize_to_file(text, voice, rate, pitch, str(audio_path))

    # Generate word timestamps (approximate: distribute evenly)
    if ts_path.exists():
        with open(ts_path, "r", encoding="utf-8") as f:
            timestamps = json.load(f)
    else:
        timestamps = _generate_timestamps(text, audio_path)
        with open(ts_path, "w", encoding="utf-8") as f:
            json.dump(timestamps, f, ensure_ascii=False)

    # Estimate duration from file size (MP3: ~16 KB/s at 128kbps for speech)
    file_size = audio_path.stat().st_size
    duration_ms = int(file_size / 16)  # rough estimate ms

    return {
        "audio_url": f"/api/tts/audio/{audio_filename}",
        "duration_ms": duration_ms,
        "word_timestamps": timestamps,
    }


def _generate_timestamps(text: str, audio_path: Path) -> list:
    """Generate approximate word timestamps by distributing text evenly over audio duration"""
    file_size = audio_path.stat().st_size
    total_duration_ms = max(file_size / 16, 500)  # rough ms estimate

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
