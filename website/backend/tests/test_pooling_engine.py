"""
Vyapar Setu — Pooling Engine Service Unit & Integration Tests
===============================================================
Tests pairwise PSU cargo pooling, economy of scale savings, joint port feasibility checks,
and CSV upload batch parsing.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.pooling_engine import (
    DemandLot,
    analyze,
    analyze_from_csv,
    VESSEL_RATE_USD_PER_T,
)


class TestPoolingEngineDetailed:
    def test_sail_rinl_paradip_pooling_economy_of_scale(self):
        """Pooling 55,000 MT (SAIL) and 60,000 MT (RINL) to Paradip should yield positive savings."""
        lot_a = DemandLot(psu_name="SAIL", cargo_tonnes=55_000, destination_port="Paradip")
        lot_b = DemandLot(psu_name="RINL", cargo_tonnes=60_000, destination_port="Paradip")

        res = analyze(lot_a, lot_b)
        assert res.feasible is True
        assert res.recommendation == "pool"
        assert res.saving_usd > 0
        assert res.saving_inr > 0
        assert res.saving_pct > 0
        assert res.pooled_vessel_class == "Capesize"

    def test_infeasible_port_dwt_limit_tuticorin(self):
        """Combining 55k and 58k tonnes to Tuticorin (60k DWT limit) must be marked infeasible."""
        lot_a = DemandLot(psu_name="SAIL", cargo_tonnes=55_000, destination_port="Tuticorin")
        lot_b = DemandLot(psu_name="RINL", cargo_tonnes=58_000, destination_port="Tuticorin")

        res = analyze(lot_a, lot_b)
        assert res.feasible is False
        assert res.recommendation == "separate"

    def test_pro_rata_cost_split_correctness(self):
        """Pro-rata cost split between lot_a and lot_b must sum up to total pooled cost."""
        lot_a = DemandLot(psu_name="SAIL", cargo_tonnes=40_000, destination_port="Paradip")
        lot_b = DemandLot(psu_name="RINL", cargo_tonnes=80_000, destination_port="Paradip")

        res = analyze(lot_a, lot_b)
        if res.feasible:
            assert abs((res.lot_a_pooled_share_usd + res.lot_b_pooled_share_usd) - res.pooled_cost_usd) < 1.0
            assert abs(res.lot_a_pooled_share_usd * 2 - res.lot_b_pooled_share_usd) < 100.0


    def test_csv_batch_parsing_multiple_pairs(self):
        """Batch CSV analysis should group rows by destination port and commodity into pairs."""
        rows = [
            {"psu_name": "SAIL", "cargo_tonnes": "55000", "destination_port": "Paradip", "commodity": "Coking Coal"},
            {"psu_name": "RINL", "cargo_tonnes": "60000", "destination_port": "Paradip", "commodity": "Coking Coal"},
            {"psu_name": "NMDC", "cargo_tonnes": "35000", "destination_port": "Vishakhapatnam", "commodity": "Iron Ore"},
            {"psu_name": "NTPC", "cargo_tonnes": "40000", "destination_port": "Vishakhapatnam", "commodity": "Iron Ore"},
        ]
        results = analyze_from_csv(rows)
        assert isinstance(results, list)
        assert len(results) == 2
        for r in results:
            assert "recommendation" in r
            assert "saving_usd" in r
