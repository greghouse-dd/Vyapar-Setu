"""
Vyapar Setu — Tender Generator Unit & Integration Tests
========================================================
Tests MSTC-compliant DOCX Tender Specification generation and vernacular ZIP generation.
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.tender_generator import generate_tender_docx, generate_vernacular_zip


class TestTenderGeneratorDetailed:
    @pytest.fixture
    def sample_recommendation(self):
        return {
            "vessel_class": "Panamax",
            "timing": "fix_now",
            "origin": "Australia",
            "lot_size_tonnes": 65000,
            "n_voyages": 1,
            "voyage_days": 35,
            "freight_cost_usd": 1200000,
            "demurrage_cost_usd": 18000,
            "quality_penalty_usd": 0,
            "total_cost_usd": 1218000,
            "total_cost_inr": 101703000,
            "cost_per_tonne_usd": 18.74,
            "cost_per_tonne_inr": 1564.0,
            "rationale": "Panamax single voyage from Australia. fix_now recommended.",
        }

    @pytest.fixture
    def sample_shap(self):
        return [
            {"driver": "Freight rate", "contribution_usd": 1200000, "contribution_pct": 98.5, "direction": "positive"},
            {"driver": "Demurrage risk", "contribution_usd": 18000, "contribution_pct": 1.5, "direction": "positive"},
        ]

    def test_generate_tender_docx_valid_content(self, sample_recommendation, sample_shap):
        """generate_tender_docx should produce valid Word (.docx) binary document."""
        payload = {"destination_port": "Paradip", "cargo_tonnes": 65000}
        doc_bytes = generate_tender_docx(sample_recommendation, sample_shap, payload)

        assert isinstance(doc_bytes, bytes)
        assert len(doc_bytes) > 2000  # Valid docx file is >2KB

    def test_generate_vernacular_zip_contains_expected_files(self, sample_recommendation, sample_shap):
        """generate_vernacular_zip should return a valid ZIP containing English + Regional docs."""
        payload = {"destination_port": "Paradip", "cargo_tonnes": 65000}
        eng_bytes = generate_tender_docx(sample_recommendation, sample_shap, payload)

        zip_bytes = generate_vernacular_zip(eng_bytes, "Paradip")
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 2000

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            namelist = z.namelist()
            assert len(namelist) >= 2
            # Should have English doc + Regional (Odia for Paradip)
            assert any("english" in name.lower() for name in namelist)
            assert any("odia" in name.lower() or "regional" in name.lower() for name in namelist)
