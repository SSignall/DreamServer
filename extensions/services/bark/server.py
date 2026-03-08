"""
Bark TTS API Server
Wraps suno-ai/bark with a minimal FastAPI HTTP interface.
Compatible with the Dream Server extensions ecosystem.
"""

import os
import io
import base64
import logging
from typing import Optional

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bark-server")

app = FastAPI(title="Bark TTS API", version="0.1.5")

# Global model state — loaded on first request to avoid startup delay
_models_loaded = False

def _load_models():
    global _models_loaded
    if not _models_loaded:
        logger.info("Loading Bark models (first request — may take a few minutes)...")
        from bark import preload_models
        preload_models()
        _models_loaded = True
        logger.info("Bark models loaded.")


class TTSRequest(BaseModel):
    text: str
    voice_preset: Optional[str] = "v2/en_speaker_6"
    output_format: Optional[str] = "wav"  # wav or mp3


class TTSResponse(BaseModel):
    audio_base64: str
    sample_rate: int
    format: str


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": _models_loaded}


@app.post("/tts", response_model=TTSResponse)
def text_to_speech(req: TTSRequest):
    """
    Generate speech audio from text using Bark.

    Args:
        text: The text to synthesize (supports [laughter], [sighs], etc.)
        voice_preset: Bark voice preset (e.g. v2/en_speaker_6)
        output_format: wav or mp3

    Returns:
        Base64-encoded audio with sample rate.
    """
    try:
        _load_models()
        from bark import generate_audio, SAMPLE_RATE

        audio_array = generate_audio(req.text, history_prompt=req.voice_preset)

        buf = io.BytesIO()
        sf.write(buf, audio_array, SAMPLE_RATE, format=req.output_format.upper())
        buf.seek(0)
        audio_b64 = base64.b64encode(buf.read()).decode("utf-8")

        return TTSResponse(
            audio_base64=audio_b64,
            sample_rate=SAMPLE_RATE,
            format=req.output_format,
        )
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts/stream")
def text_to_speech_stream(req: TTSRequest):
    """
    Generate speech and return raw audio bytes (wav).
    Suitable for streaming to audio players.
    """
    try:
        _load_models()
        from bark import generate_audio, SAMPLE_RATE

        audio_array = generate_audio(req.text, history_prompt=req.voice_preset)

        buf = io.BytesIO()
        sf.write(buf, audio_array, SAMPLE_RATE, format="WAV")
        buf.seek(0)

        return Response(
            content=buf.read(),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=bark_output.wav"},
        )
    except Exception as e:
        logger.error(f"TTS stream failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voices")
def list_voices():
    """List available Bark voice presets."""
    voices = {
        "english": [f"v2/en_speaker_{i}" for i in range(10)],
        "german": [f"v2/de_speaker_{i}" for i in range(10)],
        "spanish": [f"v2/es_speaker_{i}" for i in range(10)],
        "french": [f"v2/fr_speaker_{i}" for i in range(10)],
        "hindi": [f"v2/hi_speaker_{i}" for i in range(10)],
        "italian": [f"v2/it_speaker_{i}" for i in range(10)],
        "japanese": [f"v2/ja_speaker_{i}" for i in range(10)],
        "korean": [f"v2/ko_speaker_{i}" for i in range(10)],
        "polish": [f"v2/pl_speaker_{i}" for i in range(10)],
        "portuguese": [f"v2/pt_speaker_{i}" for i in range(10)],
        "russian": [f"v2/ru_speaker_{i}" for i in range(10)],
        "turkish": [f"v2/tr_speaker_{i}" for i in range(10)],
        "chinese": [f"v2/zh_speaker_{i}" for i in range(10)],
    }
    return voices
