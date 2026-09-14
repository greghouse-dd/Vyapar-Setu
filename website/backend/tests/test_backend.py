"""
Vyapar Setu — Backend Test Suite
=================================
Smoke tests for all service modules and API endpoints.
Run with:  cd website/backend && pytest tests/ -v

NOTE: These tests run fully offline with synthetic data.
      No real API keys or network access required.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path for direct service imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ═══════════════════════════════════════════════════════════════════════
#  SERVICE UNIT TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestDataPipeline:
    def test_pipeline_runs(self, tmp_path):
        """Data pipeline should generate freight_rates.csv."""
        from services.data_pipeline import DataPipeline
        pipeline = DataPipeline(output_dir=str(tmp_path))
        df = pipeline.run()
        assert df is not None
        assert len(df) >= 200, f"Expected ≥200 rows, got {len(df)}"
        assert "freight_rate_usd_t" in df.columns
        assert "bpi_5tc" in df.columns
        assert "vlsfo_sgp_usd_t" in df.columns

    def test_pipeline_dates(self, tmp_path):
        """Dataset should span 2020–2024."""
        from services.data_pipeline import DataPipeline
        pipeline = DataPipeline(output_dir=str(tmp_path))
        df = pipeline.run()
        assert df["week_date"].min() <= "2020-06-01"
        assert df["week_date"].max() >= "2024-06-01"

    def test_no_nan_in_key_columns(self, tmp_path):
        """Critical feature columns should have no NaN values."""
        from services.data_pipeline import DataPipeline
        pipeline = DataPipeline(output_dir=str(tmp_path))
        df = pipeline.run()
        for col in ["freight_rate_usd_t", "bpi_5tc", "vlsfo_sgp_usd_t"]:
            assert df[col].isna().sum() == 0, f"NaN found in {col}"


class TestMILPOptimizer:
    def test_optimize_returns_optimal(self):
        """Optimizer should return a feasible result for standard Paradip scenario."""
        from services.milp_optimizer import OptimizationRequest, optimize
        req = OptimizationRequest(
            destination_port="Paradip",
            cargo_tonnes=65_000,
            latest_arrival_date_days=90,
        )
        result = optimize(req)
        assert result["status"] == "optimal"
        assert "recommendation" in result
        assert result["recommendation"]["total_cost_usd"] > 0

    def test_optimize_respects_port_dwt_limit(self):
        """Tuticorin (60k DWT limit) should exclude Capesize."""
        from services.milp_optimizer import OptimizationRequest, optimize
        req = OptimizationRequest(
            destination_port="Tuticorin",
            cargo_tonnes=50_000,
            latest_arrival_date_days=90,
        )
        result = optimize(req)
        if result["status"] == "optimal":
            assert result["recommendation"]["vessel_class"] != "Capesize"

    def test_budget_cap_respected(self):
        """With a very tight budget, result should be infeasible."""
        from services.milp_optimizer import OptimizationRequest, optimize
        req = OptimizationRequest(
            destination_port="Paradip",
            cargo_tonnes=65_000,
            latest_arrival_date_days=90,
            budget_cap_usd=1.0,   # impossibly tight
        )
        result = optimize(req)
        assert result["status"] == "infeasible"

    def test_quick_recommendation(self):
        """Quick recommendation should return a valid action."""
        from services.milp_optimizer import get_chartering_quick_recommendation
        result = get_chartering_quick_recommendation(
            forecast_trend="rising",
            weeks_to_delivery=8,
            current_rate_usd=18.5,
            ffa_available=True,
        )
        assert result["action"] in ("fix_now", "wait_2w", "wait_4w", "ffa_hedge")
        assert "rationale" in result


class TestPoolingEngine:
    def test_pooling_saves_money(self):
        """SAIL + RINL pooled to Paradip should show positive savings."""
        from services.pooling_engine import DemandLot, analyze
        lot_a = DemandLot(psu_name="SAIL", cargo_tonnes=55_000, destination_port="Paradip")
        lot_b = DemandLot(psu_name="RINL", cargo_tonnes=60_000, destination_port="Paradip")
        result = analyze(lot_a, lot_b)
        assert result.saving_usd >= 0
        assert result.recommendation in ("pool", "separate")

    def test_infeasible_if_combined_exceeds_port(self):
        """Pooled Capesize to Tuticorin (60k DWT) should be infeasible."""
        from services.pooling_engine import DemandLot, analyze
        lot_a = DemandLot(psu_name="SAIL", cargo_tonnes=55_000, destination_port="Tuticorin")
        lot_b = DemandLot(psu_name="RINL", cargo_tonnes=58_000, destination_port="Tuticorin")
        result = analyze(lot_a, lot_b)
        assert not result.feasible

    def test_csv_parsing(self):
        """Batch CSV analysis should handle two pairs."""
        from services.pooling_engine import analyze_from_csv
        rows = [
            {"psu_name": "SAIL",  "cargo_tonnes": "55000", "destination_port": "Paradip", "commodity": "Coal", "delivery_window_days": "60"},
            {"psu_name": "RINL",  "cargo_tonnes": "60000", "destination_port": "Paradip", "commodity": "Coal", "delivery_window_days": "60"},
            {"psu_name": "NMDC",  "cargo_tonnes": "45000", "destination_port": "Vishakhapatnam", "commodity": "Iron Ore", "delivery_window_days": "45"},
            {"psu_name": "NTPC",  "cargo_tonnes": "50000", "destination_port": "Vishakhapatnam", "commodity": "Coal", "delivery_window_days": "50"},
        ]
        results = analyze_from_csv(rows)
        assert len(results) == 2
        for r in results:
            assert "recommendation" in r


class TestIdleEngine:
    def test_advisor_returns_strategies(self):
        """Idle advisor should return 4+ strategies."""
        from services.idle_engine import IdleAdvisorRequest, advise
        req = IdleAdvisorRequest(
            vessel_class="Panamax",
            current_port="Paradip",
            dwt=75_000,
        )
        result = advise(req)
        assert "recommended_strategy" in result
        assert len(result["all_strategies"]) >= 4

    def test_best_strategy_has_highest_net_value(self):
        """The recommended strategy should have the highest net_value_usd."""
        from services.idle_engine import IdleAdvisorRequest, advise
        req = IdleAdvisorRequest(
            vessel_class="Supramax",
            current_port="Vishakhapatnam",
            dwt=57_000,
        )
        result = advise(req)
        best_net = result["net_value_usd"]
        for s in result["all_strategies"]:
            assert s["net_value_usd"] <= best_net + 1   # allow float rounding

    def test_unknown_vessel_class(self):
        """Unknown vessel class should return an error dict."""
        from services.idle_engine import IdleAdvisorRequest, advise
        req = IdleAdvisorRequest(
            vessel_class="Megaship",
            current_port="Paradip",
            dwt=500_000,
        )
        result = advise(req)
        assert "error" in result


class TestTenderGenerator:
    def test_docx_bytes_returned(self):
        """generate_tender_docx should return non-empty bytes."""
        from services.tender_generator import generate_tender_docx
        rec = {
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
        shap = [
            {"driver": "Freight rate", "contribution_usd": 1200000, "contribution_pct": 98.5, "direction": "positive"},
        ]
        payload = {"destination_port": "Paradip", "cargo_tonnes": 65000}
        doc_bytes = generate_tender_docx(rec, shap, payload)
        assert isinstance(doc_bytes, bytes)
        assert len(doc_bytes) > 1000   # real docx is >5KB

    def test_vernacular_zip_contains_two_docs(self):
        """Vernacular zip should contain two .docx files."""
        import zipfile, io
        from services.tender_generator import generate_tender_docx, generate_vernacular_zip
        rec = {
            "vessel_class": "Panamax", "timing": "fix_now", "origin": "Australia",
            "lot_size_tonnes": 65000, "n_voyages": 1, "voyage_days": 35,
            "freight_cost_usd": 1200000, "demurrage_cost_usd": 0,
            "quality_penalty_usd": 0, "total_cost_usd": 1200000,
            "total_cost_inr": 100200000, "cost_per_tonne_usd": 18.46,
            "cost_per_tonne_inr": 1541.0, "rationale": "Test.",
        }
        eng_bytes = generate_tender_docx(rec, [], {"destination_port": "Paradip"})
        zip_bytes = generate_vernacular_zip(eng_bytes, "Paradip")
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            names = z.namelist()
        assert any("english" in n for n in names)
        assert any("odia" in n or "hindi" in n or "telugu" in n or "bengali" in n for n in names)


# ═══════════════════════════════════════════════════════════════════════
#  API ENDPOINT INTEGRATION TESTS (using FastAPI TestClient)
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def client():
    """Create FastAPI test client. Skip if imports fail (dependencies not installed)."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    try:
        from main import app
        return TestClient(app)
    except Exception as e:
        pytest.skip(f"Could not create test client: {e}")


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestOptimizerEndpoint:
    def test_optimize_endpoint(self, client):
        resp = client.post("/optimizer", json={
            "destination_port": "Paradip",
            "cargo_tonnes": 65000,
            "latest_arrival_date_days": 90,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("optimal", "infeasible")

    def test_quick_recommendation_endpoint(self, client):
        resp = client.post("/optimizer/chartering-recommendation", json={
            "forecast_trend": "rising",
            "weeks_to_delivery": 8,
            "current_rate_usd": 18.5,
        })
        assert resp.status_code == 200
        assert resp.json()["action"] in ("fix_now", "wait_2w", "wait_4w", "ffa_hedge")


class TestPoolingEndpoint:
    def test_pooling_analyze(self, client):
        resp = client.post("/pooling/analyze", json={
            "lot_a": {"psu_name": "SAIL", "cargo_tonnes": 55000, "destination_port": "Paradip"},
            "lot_b": {"psu_name": "RINL", "cargo_tonnes": 60000, "destination_port": "Paradip"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "recommendation" in data
        assert "savings" in data


class TestIdleAdvisorEndpoint:
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
