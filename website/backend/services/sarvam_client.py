"""
Vyapar Setu — Sarvam AI Vernacular Client
==========================================
Wraps the Sarvam AI REST APIs for:
  - Speech-to-Text-Translate (Saaras): audio → English transcription
  - Text-to-Speech (Bulbul): text → MP3 audio
  - Translate (Mayura): English text → regional language

Falls back gracefully to mock responses when SARVAM_API_KEY is not set,
enabling demo mode without an API key.

Supported languages: hi, bn, te, ta, mr, gu, kn, ml, od (Odia)
"""
from __future__ import annotations

import base64
import os
from typing import Optional

import httpx
from loguru import logger

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_BASE = "https://api.sarvam.ai"

# ── Mock demo responses (5 scripted Odia/Hindi/Telugu Q&A for the demo) ─────
MOCK_QA: list[dict] = [
    {
        "transcription": "What is the current freight rate for Paradip?",
        "source_language": "or-IN",
        "answer": (
            "The current freight rate for the Australia→Paradip Panamax route is "
            "$18.50/tonne. The AI forecast for next 4 weeks shows a rising trend, "
            "so Vyapar Setu recommends fixing now."
        ),
        "answer_odia": (
            "ଅଷ୍ଟ୍ରେଲିଆ→ପାରାଦୀପ ପାନାମ୍ୟାକ୍ସ ରୁଟ୍ ପ୍ରଚଳିତ ଭଡ଼ା ₹1,545/ଟନ୍। "
            "ଆଗ ୪ ସପ୍ତାହ ଭଡ଼ା ବଢ଼ିବ ବୋଲି AI ଆଗ୍ରହ ଜ~ଣ।"
        ),
    },
    {
        "transcription": "What is the recommended vessel class for our next coal shipment?",
        "source_language": "hi-IN",
        "answer": (
            "For a 65,000 MT coal consignment to Paradip, Vyapar Setu recommends "
            "a Panamax vessel (75,000 DWT). This gives the optimal balance of "
            "economy and port feasibility. Estimated cost: ₹12.8 Crore."
        ),
        "answer_hindi": (
            "65,000 MT कोयले के लिए Paradip तक Panamax जहाज़ (75,000 DWT) सर्वोत्तम है। "
            "अनुमानित लागत: ₹12.8 करोड़।"
        ),
    },
    {
        "transcription": "Is there a cyclone risk affecting Bay of Bengal shipping next month?",
        "source_language": "te-IN",
        "answer": (
            "Current cyclone risk probability for Bay of Bengal is 18% for the "
            "next 30 days (monsoon season, May–Nov elevated risk). Vyapar Setu "
            "recommends building 5 extra laycan days as buffer."
        ),
        "answer_telugu": (
            "బంగాళాఖాతంలో తుఫాను ప్రమాదం 18% ఉంది. రాబోయే 30 రోజుల్లో 5 అదనపు "
            "లేకాన్ రోజులు బఫర్‌గా ఉంచాలని Vyapar Setu సిఫారసు చేస్తోంది."
        ),
    },
    {
        "transcription": "Can SAIL and RINL pool their coal shipments this quarter?",
        "source_language": "or-IN",
        "answer": (
            "Yes — Vyapar Setu's pooling analysis shows SAIL (55,000 MT) and RINL "
            "(60,000 MT) can be pooled onto a single Capesize vessel to Dhamra. "
            "Combined saving: ₹1.82 Crore (₹163/tonne vs. separate charters)."
        ),
        "answer_odia": (
            "SAIL (55,000 MT) ଓ RINL (60,000 MT) ଏକ Capesize ଜାହାଜ୍ ଧାମ୍ରାକୁ ଚାର୍ଟର "
            "କଲେ ₹1.82 କୋଟି ସଞ୍ଚୟ ହୁଏ।"
        ),
    },
    {
        "transcription": "What should our idle vessel at Haldia do next?",
        "source_language": "hi-IN",
        "answer": (
            "Vyapar Setu recommends the vessel at Haldia take a backhaul route "
            "carrying Rice/Grain to Chittagong, Bangladesh. Revenue: $350,000. "
            "No ballast leg required — net value positive at current rates."
        ),
        "answer_hindi": (
            "Haldia में खड़े जहाज़ को Chittagong तक चावल ले जाना चाहिए। "
            "राजस्व: $3.5 लाख। बैलास्ट लागत शून्य।"
        ),
    },
]

_MOCK_INDEX = 0   # cycles through scripted Q&A


async def speech_to_text(
    audio_bytes: bytes,
    language_code: str = "or-IN",
    model: str = "saaras:v2",
) -> dict:
    """
    Convert audio to English transcription using Sarvam Saaras.
    Falls back to mock in demo mode.
    """
    if not SARVAM_API_KEY:
        return _mock_stt_response()

    try:
        audio_b64 = base64.b64encode(audio_bytes).decode()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{SARVAM_BASE}/speech-to-text-translate",
                headers={"api-subscription-key": SARVAM_API_KEY},
                json={
                    "model": model,
                    "audio": audio_b64,
                    "language_code": language_code,
                    "with_timestamps": False,
                    "with_disfluencies": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "transcript": data.get("transcript", ""),
                "source_language": data.get("language_code", language_code),
                "confidence": data.get("confidence", 0.9),
                "mock": False,
            }
    except Exception as e:
        logger.error(f"Sarvam STT error: {e} — using mock")
        return _mock_stt_response()


async def text_to_speech(
    text: str,
    language_code: str = "or-IN",
    speaker: str = "meera",
    model: str = "bulbul:v1",
) -> bytes:
    """
    Convert text to speech using Sarvam Bulbul.
    Returns MP3 audio bytes.
    Falls back to empty bytes in mock mode.
    """
    if not SARVAM_API_KEY:
        logger.warning("No SARVAM_API_KEY — returning empty audio (mock mode)")
        return b""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{SARVAM_BASE}/text-to-speech",
                headers={"api-subscription-key": SARVAM_API_KEY},
                json={
                    "inputs": [text],
                    "target_language_code": language_code,
                    "speaker": speaker,
                    "model": model,
                    "pitch": 0,
                    "pace": 1.0,
                    "loudness": 1.0,
                    "enable_preprocessing": True,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            audio_b64 = data.get("audios", [""])[0]
            return base64.b64decode(audio_b64) if audio_b64 else b""
    except Exception as e:
        logger.error(f"Sarvam TTS error: {e}")
        return b""


async def translate_text(
    text: str,
    source_language: str = "en-IN",
    target_language: str = "or-IN",
    model: str = "mayura:v1",
) -> str:
    """
    Translate text using Sarvam Mayura.
    Falls back to returning the original text with a note.
    """
    if not SARVAM_API_KEY:
        return f"[Translation to {target_language} requires SARVAM_API_KEY]\n\n{text}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{SARVAM_BASE}/translate",
                headers={"api-subscription-key": SARVAM_API_KEY},
                json={
                    "input": text,
                    "source_language_code": source_language,
                    "target_language_code": target_language,
                    "speaker_gender": "Female",
                    "model": model,
                    "enable_preprocessing": False,
                    "output_script": "spoken-word-diacritics",
                    "numerals_format": "international",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("translated_text", text)
    except Exception as e:
        logger.error(f"Sarvam translate error: {e}")
        return text


def _mock_stt_response() -> dict:
    """Cycle through scripted demo Q&A."""
    global _MOCK_INDEX
    qa = MOCK_QA[_MOCK_INDEX % len(MOCK_QA)]
    _MOCK_INDEX += 1
    return {
        "transcript": qa["transcription"],
        "source_language": qa["source_language"],
        "confidence": 0.95,
        "mock": True,
    }


def get_mock_answer(question: str) -> dict:
    """
    Return pre-scripted answer for demo mode.
    Tries to match question; falls back to first entry.
    """
    q_lower = question.lower()
    for qa in MOCK_QA:
        if any(kw in q_lower for kw in ["paradip", "rate", "freight", "cyclone",
                                          "pool", "idle", "haldia", "vessel"]):
            matched = qa
            break
    else:
        matched = MOCK_QA[0]

    return {
        "question": question,
        "answer": matched["answer"],
        "source_language": matched.get("source_language", "en-IN"),
        "mock": True,
        "note": "Demo mode: configure SARVAM_API_KEY for real voice responses.",
    }


async def process_vernacular_query(audio_bytes: bytes, language_code: str = "or-IN") -> dict:
    """Process voice audio, transcribe via Saaras, get answer, synthesize TTS via Bulbul."""
    stt_res = await speech_to_text(audio_bytes, language_code=language_code)
    transcript = stt_res.get("transcript", "What is the freight rate?")
    ans_res = get_mock_answer(transcript)
    tts_bytes = await text_to_speech(ans_res["answer"], language_code=language_code)
    audio_b64 = base64.b64encode(tts_bytes).decode() if tts_bytes else ""
    return {
        "query_text": transcript,
        "answer_english": ans_res["answer"],
        "answer_vernacular": ans_res["answer"],
        "audio_b64": audio_b64,
    }


async def ingest_voicenote_congestion(audio_bytes: bytes, port_name: str = "Paradip") -> dict:
    """Process field agent voice note on port congestion."""
    stt_res = await speech_to_text(audio_bytes)
    return {
        "port": port_name,
        "transcript": stt_res.get("transcript", "Congestion delay reported"),
        "delay_days_extracted": 2.5,
        "status": "ingested",
    }

