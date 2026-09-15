"""
Vyapar Setu — Forecaster Service Unit & Integration Tests
==========================================================
Tests Prophet + XGBoost Ensemble, P10/P50/P90 uncertainty intervals,
SHAP drivers, backtest evaluation metrics, and IMD cyclone risk overrides.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np
from services.forecaster import FreightForecaster, get_forecaster


class TestFreightForecaster:
    @pytest.fixture(scope="class")
    def forecaster(self):
        """Fixture providing a trained forecaster instance."""
        f = FreightForecaster()
        f.train(force_retrain=False)
        return f

    def test_forecaster_initialization(self, forecaster):
        """Forecaster should initialize and train or load existing models."""
        assert forecaster.is_trained

    def test_forecast_horizons_structure(self, forecaster):
        """Predicting 12 weeks ahead should yield P10, P50, and P90 bands."""
        res = forecaster.predict(horizon_weeks=12)
        assert "forecasts" in res
        forecasts = res["forecasts"]
        assert len(forecasts) == 12

        for step in forecasts:
            assert "week" in step
            assert "p10" in step
            assert "p50" in step
            assert "p90" in step
            # Uncertainty Interval Guarantee: P10 <= P50 <= P90
            assert step["p10"] <= step["p50"] + 1e-5
            assert step["p50"] <= step["p90"] + 1e-5
            assert step["p50"] > 0

    def test_shap_drivers_generation(self, forecaster):
        """Forecaster should produce top SHAP drivers with valid contributions."""
        res = forecaster.predict(horizon_weeks=4)
        assert "shap_drivers" in res
        drivers = res["shap_drivers"]
        assert isinstance(drivers, list)
        assert len(drivers) > 0

        for driver in drivers:
            assert "feature" in driver or "description" in driver
            assert "direction" in driver
            assert driver["direction"] in ("positive", "negative")


    def test_backtest_evaluation(self, forecaster):
        """Backtest logic should calculate MAPE, RMSE, and headline savings."""
        bt = forecaster.backtest(test_weeks=26)
        assert "mape" in bt
        assert "rmse" in bt
        assert "savings_inr_per_tonne" in bt
        assert "headline_savings_pct" in bt
        assert bt["mape"] >= 0
        assert bt["rmse"] >= 0

    def test_cyclone_override_risk_bumping(self, forecaster):
        """IMD cyclone category >= 3 should trigger a risk override flag."""
        res_normal = forecaster.predict(horizon_weeks=4, cyclone_category=0)
        res_cyclone = forecaster.predict(horizon_weeks=4, cyclone_category=4)

        assert res_cyclone.get("cyclone_override_active") is True
        assert res_cyclone["forecasts"][0]["p90"] >= res_normal["forecasts"][0]["p90"]

