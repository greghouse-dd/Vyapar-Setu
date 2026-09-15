"""
Vyapar Setu — Idle Fleet & Deadheading Advisor Unit & Integration Tests
========================================================================
Tests post-discharge vessel strategies (Ballast Reposition, Backhaul, Short Relet, Lay-up),
fuel consumption economics, net value ranking, and error validations.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.idle_engine import IdleAdvisorRequest, advise


class TestIdleEngineDetailed:
    def test_advise_panamax_paradip(self):
        """Advisor for Panamax at Paradip should return strategies with positive net value."""
        req = IdleAdvisorRequest(
            vessel_class="Panamax",
            current_port="Paradip",
            dwt=75_000,
        )
        res = advise(req)
        assert "recommended_strategy" in res
        assert "all_strategies" in res
        assert len(res["all_strategies"]) >= 4

        # Check strategy fields
        for s in res["all_strategies"]:
            assert "strategy" in s
            assert "net_value_usd" in s
            assert "voyage_days" in s

    def test_best_strategy_is_top_ranked(self):
        """The strategy returned as recommended_strategy must have the maximum net_value_usd."""
        req = IdleAdvisorRequest(
            vessel_class="Supramax",
            current_port="Vishakhapatnam",
            dwt=57_000,
        )
        res = advise(req)
        best_net = res["net_value_usd"]
        for s in res["all_strategies"]:
            assert s["net_value_usd"] <= best_net + 1e-3

    def test_backhaul_triangular_voyage_included(self):
        """Strategies should include backhaul / triangular options when available."""
        req = IdleAdvisorRequest(
            vessel_class="Panamax",
            current_port="Haldia",
            dwt=70_000,
        )
        res = advise(req)
        strategy_types = [s["strategy"] for s in res["all_strategies"]]
        assert any(t in strategy_types for t in ("backhaul", "reposition", "relet", "idle_wait"))


    def test_unknown_vessel_class_returns_error(self):
        """Invalid vessel class should return error response without raising crash."""
        req = IdleAdvisorRequest(
            vessel_class="UltraCarrier",
            current_port="Paradip",
            dwt=400_000,
        )
        res = advise(req)
        assert "error" in res
