"""
Vyapar Setu — Vernacular AI Router
=====================================
Endpoints:
  POST /voice-query        → Audio bytes → transcription → answer → audio bytes
  POST /translate-tender   → English text → translated text in target language
  POST /voice-note-ingest  → Field agent audio → structured congestion event
"""
from __future__ import annotations

import base64
import traceback
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel, Field

from services import sarvam_client

router = APIRouter(prefix="/vernacular", tags=["Vernacular"])

# ── Supported language codes ──────────────────────────────────────────────────
LANGUAGE_CODES = {
    "odia":    "or-IN",
    "hindi":   "hi-IN",
    "telugu":  "te-IN",
    "bengali": "bn-IN",
    "tamil":   "ta-IN",
    "marathi": "mr-IN",
    "gujarati":"gu-IN",
}


class TranslateRequest(BaseModel):
    text: str = Field(description="English text to translate")
    target_language: str = Field(
        default="Odia",
        description="Target language: Odia | Hindi | Telugu | Bengali | Tamil",
    )
    source_language: str = Field(default="en-IN")


class VoiceQueryTextRequest(BaseModel):
    """For testing without audio upload — pass transcript directly."""
    transcript: str = Field(description="User question in any language")
    respond_in_language: str = Field(default="Hindi")


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/voice-query", summary="Audio → transcription → answer → audio response")
async def voice_query(
    audio: UploadFile = File(..., description="Audio file (WAV/MP3/OGG)"),
    language_code: str = Form(default="or-IN", description="Speaker language code"),
    respond_in_language: str = Form(default="or-IN", description="Response audio language"),
) -> dict:
    try:
        audio_bytes = await audio.read()

        # 1. Speech to text
        stt_result = await sarvam_client.speech_to_text(
            audio_bytes=audio_bytes,
            language_code=language_code,
        )
        transcript = stt_result.get("transcript", "")

        # 2. Generate answer (mock for demo — in production: call LLM with domain context)
        answer_data = sarvam_client.get_mock_answer(transcript)
        answer_text = answer_data["answer"]

        # 3. Text to speech
        tts_audio_bytes = await sarvam_client.text_to_speech(
            text=answer_text,
            language_code=respond_in_language,
        )

        return {
            "transcript": transcript,
            "source_language": stt_result.get("source_language"),
            "confidence": stt_result.get("confidence"),
            "answer": answer_text,
            "audio_base64": base64.b64encode(tts_audio_bytes).decode() if tts_audio_bytes else None,
            "audio_available": len(tts_audio_bytes) > 0,
            "mock": stt_result.get("mock", False),
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-query/text", summary="Text question → answer (no audio upload needed)")
async def voice_query_text(req: VoiceQueryTextRequest) -> dict:
    try:
        answer_data = sarvam_client.get_mock_answer(req.transcript)
        target_lang_code = LANGUAGE_CODES.get(req.respond_in_language.lower(), "hi-IN")

        # Translate answer if Sarvam API key is set
        translated = await sarvam_client.translate_text(
            text=answer_data["answer"],
            source_language="en-IN",
            target_language=target_lang_code,
        )

        return {
            "transcript": req.transcript,
            "answer_english": answer_data["answer"],
            "answer_translated": translated,
            "target_language": req.respond_in_language,
            "mock": answer_data.get("mock", True),
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-tender", summary="Translate tender text to a regional language")
async def translate_tender(req: TranslateRequest) -> dict:
    try:
        target_lang_code = LANGUAGE_CODES.get(req.target_language.lower(), "hi-IN")
        translated = await sarvam_client.translate_text(
            text=req.text,
            source_language=req.source_language,
            target_language=target_lang_code,
        )
        return {
            "original": req.text,
            "translated": translated,
            "source_language": req.source_language,
            "target_language": req.target_language,
            "target_language_code": target_lang_code,
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-note-ingest", summary="Field agent audio note → structured congestion event")
async def voice_note_ingest(
    audio: UploadFile = File(...),
    port: str = Form(default="Paradip"),
    language_code: str = Form(default="or-IN"),
) -> dict:
    """
    Ingests a field agent voice note reporting port congestion / berth unavailability.
    Transcribes, extracts structured data, and (in production) updates the feature store.
    """
    try:
        audio_bytes = await audio.read()
        stt_result = await sarvam_client.speech_to_text(
            audio_bytes=audio_bytes,
            language_code=language_code,
        )
        transcript = stt_result.get("transcript", "")

        # Mock structured extraction (in production: use an LLM to parse the text)
        event = {
            "port": port,
            "transcript": transcript,
            "extracted_event": {
                "event_type": "berth_congestion",
                "severity": "moderate",
                "estimated_delay_days": 2,
                "reported_by": "Field agent (voice note)",
                "note": "Structured extraction requires LLM integration in production.",
            },
            "feature_store_updated": False,
            "mock": stt_result.get("mock", False),
        }
        return event
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
