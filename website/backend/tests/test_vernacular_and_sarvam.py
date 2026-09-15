"""
Vyapar Setu — Vernacular AI & Sarvam Client Unit Tests
======================================================
Tests Sarvam AI integration (Saaras STT, Bulbul TTS, Mayura Translation, and Field Voice Note ingestion).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from services.sarvam_client import (
    speech_to_text,
    text_to_speech,
    translate_text,
    process_vernacular_query,
    ingest_voicenote_congestion,
)


class TestVernacularAndSarvam:
    def test_speech_to_text_mock_or_api(self):
        """STT should return valid transcript, detected language, and confidence score."""
        dummy_audio = b"MOCK_AUDIO_BYTES_FOR_STT"
        result = asyncio.run(speech_to_text(dummy_audio, language_code="or-IN"))

        assert "transcript" in result
        assert "confidence" in result
        assert len(result["transcript"]) > 0

    def test_text_to_speech_mock_or_api(self):
        """TTS should take text and return audio bytes or b64 string."""
        sample_text = "Paradip port freight forecast is rising."
        audio_res = asyncio.run(text_to_speech(sample_text, language_code="or-IN"))
        assert isinstance(audio_res, bytes)

    def test_translate_text(self):
        """translate_text should translate English text to target regional language."""
        text = "Recommended vessel class is Panamax."
        translated = asyncio.run(translate_text(text, target_language="or-IN"))

        assert isinstance(translated, str)
        assert len(translated) > 0

    def test_process_vernacular_query_full_pipeline(self):
        """process_vernacular_query should process voice audio bytes and return answer text + audio."""
        dummy_audio = b"MOCK_VOICE_QUERY_BYTES"
        res = asyncio.run(process_vernacular_query(dummy_audio, language_code="hi-IN"))

        assert "query_text" in res
        assert "answer_english" in res
        assert "answer_vernacular" in res
        assert "audio_b64" in res

    def test_ingest_voicenote_congestion_extraction(self):
        """Field agent voice note should extract port congestion delay days."""
        dummy_audio = b"MOCK_FIELD_AGENT_AUDIO"
        res = asyncio.run(ingest_voicenote_congestion(dummy_audio, port_name="Paradip"))

        assert "port" in res
        assert "delay_days_extracted" in res
        assert "status" in res
        assert res["port"] == "Paradip"

