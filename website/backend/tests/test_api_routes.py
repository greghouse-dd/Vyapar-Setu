"""
Vyapar Setu — API Integration Tests
====================================
Integration tests for all FastAPI REST endpoints using TestClient.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


class TestAPIRoutes:
    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "Vyapar Setu API"
        assert "docs" in data

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_forecast_predict_endpoint(self, client):
        resp = client.post("/forecast", json={
            "horizon_weeks": 4,
            "origin": "Australia",
            "destination": "Paradip",
            "vessel_class": "Panamax",
            "cyclone_category": 0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "forecast" in data
        assert len(data["forecast"]) == 4

    def test_forecast_backtest_endpoint(self, client):
        resp = client.get("/forecast/backtest")
        assert resp.status_code == 200
        data = resp.json()
        assert "mape_ensemble" in data

    def test_optimizer_endpoint(self, client):
        resp = client.post("/optimizer", json={
            "destination_port": "Paradip",
            "cargo_tonnes": 65000,
            "latest_arrival_date_days": 90,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("optimal", "infeasible")

    def test_chartering_recommendation_endpoint(self, client):
        resp = client.post("/optimizer/chartering-recommendation", json={
            "forecast_trend": "rising",
            "weeks_to_delivery": 8,
            "current_rate_usd": 18.5,
            "ffa_available": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["action"] in ("fix_now", "wait_2w", "wait_4w", "ffa_hedge")

    def test_pooling_analyze_endpoint(self, client):
        resp = client.post("/pooling/analyze", json={
            "lot_a": {"psu_name": "SAIL", "cargo_tonnes": 55000, "destination_port": "Paradip"},
            "lot_b": {"psu_name": "RINL", "cargo_tonnes": 60000, "destination_port": "Paradip"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendation" in data
        assert "savings" in data

    def test_idle_advisor_endpoint(self, client):
        resp = client.post("/idle-advisor", json={
            "vessel_class": "Panamax",
            "current_port": "Paradip",
            "dwt": 75000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "recommended_strategy" in data
        assert "all_strategies" in data

    def test_generate_tender_endpoint(self, client):
        resp = client.post("/generate-tender", json={
            "recommendation": {
                "vessel_class": "Panamax", "timing": "fix_now", "origin": "Australia",
                "lot_size_tonnes": 65000, "n_voyages": 1, "voyage_days": 35,
                "freight_cost_usd": 1200000, "demurrage_cost_usd": 0,
                "quality_penalty_usd": 0, "total_cost_usd": 1200000,
                "total_cost_inr": 100200000, "cost_per_tonne_usd": 18.46,
                "cost_per_tonne_inr": 1541.0, "rationale": "API Test.",
            },
            "shap_drivers": [],
            "payload": {"destination_port": "Paradip", "cargo_tonnes": 65000},
        })
        assert resp.status_code == 200
        assert resp.headers["content-type"] in (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/octet-stream"
        )
        assert len(resp.content) > 1000

    def test_vernacular_voice_query_endpoint(self, client):
        resp = client.post("/vernacular/voice-query", data={"language_code": "or-IN"}, files={"audio": ("query.wav", b"AUDIO_BYTES")})
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data or "transcript" in data

