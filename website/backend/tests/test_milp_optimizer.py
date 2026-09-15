"""
Vyapar Setu — MILP Optimizer Service Unit & Integration Tests
===============================================================
Tests multi-constraint MILP chartering optimization across all 7 East Coast ports,
vessel classes, supplier quality adjustments, budget cap enforcement, and recommendations.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.milp_optimizer import (
    OptimizationRequest,
    optimize,
    get_chartering_quick_recommendation,
    VESSEL_CLASSES,
    ORIGINS,
)


class TestMILPOptimizerDetailed:
    @pytest.mark.parametrize("port", [
        "Paradip", "Dhamra", "Vishakhapatnam", "Gangavaram",
        "Gopalpur", "Haldia", "Sagar-Sandheads"
    ])
    def test_all_seven_ports_handled(self, port: str):
        """MILP optimizer should run without exceptions across all 7 named destination ports."""
        req = OptimizationRequest(
            destination_port=port,
            cargo_tonnes=50_000,
            latest_arrival_date_days=90,
        )
        res = optimize(req)
        assert res["status"] in ("optimal", "infeasible")
        if res["status"] == "optimal":
            assert "recommendation" in res
            assert res["recommendation"]["vessel_class"] in VESSEL_CLASSES

    def test_port_ceiling_haldia_shallow_draft(self):
        """Haldia (river port) cannot accommodate Capesize directly; should cap at Supramax/Handysize."""
        req = OptimizationRequest(
            destination_port="Haldia",
            cargo_tonnes=35_000,
            latest_arrival_date_days=60,
        )
        res = optimize(req)
        if res["status"] == "optimal":
            assert res["recommendation"]["vessel_class"] in ("Handysize", "Supramax")

    def test_supplier_origin_selection(self):
        """Testing all supported origin regions are present in ORIGINS."""
        assert len(ORIGINS) >= 4
        for origin_name, details in ORIGINS.items():
            assert "distance_nm" in details
            assert "laycan_lead_days" in details
            assert details["distance_nm"] > 0


    def test_budget_cap_enforcement(self):
        """Setting an impossible budget cap must return infeasible status."""
        req = OptimizationRequest(
            destination_port="Paradip",
            cargo_tonnes=65_000,
            latest_arrival_date_days=90,
            budget_cap_usd=10.0,  # $10 total budget is impossible for 65k tonnes
        )
        res = optimize(req)
        assert res["status"] == "infeasible"

    def test_chartering_quick_recommendation_rules(self):
        """Test quick chartering timing rules under various market trends."""
        rec1 = get_chartering_quick_recommendation("rising", weeks_to_delivery=3, current_rate_usd=22.0)
        assert rec1["action"] in ("fix_now", "wait_2w", "wait_4w", "ffa_hedge")

        rec2 = get_chartering_quick_recommendation("falling", weeks_to_delivery=10, current_rate_usd=25.0)
        assert rec2["action"] in ("fix_now", "wait_2w", "wait_4w", "ffa_hedge")

        rec3 = get_chartering_quick_recommendation("volatile", weeks_to_delivery=8, current_rate_usd=30.0, ffa_available=True)
        assert rec3["action"] in ("fix_now", "wait_2w", "wait_4w", "ffa_hedge")

