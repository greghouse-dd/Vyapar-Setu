"""
Vyapar Setu — Unified Demo Scenario Service
============================================
Provides a single, coherent demo scenario that all modules consume.
This ensures the frontend feels like one integrated platform, not
seven independent demos.

Demo scenario: Australia → Paradip (Panamax, 65,000 MT, coking coal)
  → Freight Forecast (P10/P50/P90)
  → Fix / Wait / Hedge recommendation
  → Port feasibility check (7-port lookup)
  → SAIL + RINL Pooling analysis
  → Post-discharge Idle/Backhaul Advisor
  → Tender Specification generation
  → Vernacular voice Q&A
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

# ══════════════════════════════════════════════════════════════════════════════
#  DEFAULT DEMO SCENARIO PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_SCENARIO: Dict[str, Any] = {
    # Primary shipment
    "origin":          "Australia",
    "destination":     "Paradip",
    "cargo_type":      "Coking Coal (HCC)",
    "cargo_tonnes":    65_000,
    "vessel_class":    "Panamax",
    "psu_primary":     "RINL",

    # Pooling partners
    "sail_cargo_tonnes":    55_000,
    "rinl_cargo_tonnes":    60_000,
    "sail_destination":     "Dhamra",
    "rinl_destination":     "Paradip",

    # Voyage economics
    "voyage_distance_nm":   4_800,
    "vessel_speed_knots":   13.0,
    "sea_days":             15.4,
    "port_days":            4.0,
    "total_voyage_days":    19.4,
    "bunker_consumption_tpd": 28,

    # Procurement / planning
    "safety_stock_days":  30,
    "horizon_weeks":      12,
    "budget_usd_per_t":   28.0,

    # Quality specification (Australian HCC)
    "quality_specs": {
        "ash_pct_max":         10.5,
        "moisture_pct_max":    8.0,
        "volatile_matter_pct": 22.0,
        "csr_min":             62,
        "cri_max":             24,
        "fluidity_ddpm":       150,
    },

    # Idle advisor context (post-discharge)
    "post_discharge_port": "Paradip",
    "idle_horizon_weeks":  4,

    # Tender
    "freight_ceiling_usd_t": 26.0,
    "tender_psu":             "RINL",
}


def get_demo_scenario() -> Dict[str, Any]:
    """Return the current demo scenario with today's date injected."""
    scenario = DEFAULT_SCENARIO.copy()
    today = date.today()
    scenario["as_of_date"]             = today.isoformat()
    scenario["required_by_date"]       = (today + timedelta(weeks=6)).isoformat()
    scenario["delivery_window_start"]  = (today + timedelta(weeks=5)).isoformat()
    scenario["delivery_window_end"]    = (today + timedelta(weeks=7)).isoformat()
    scenario["discharge_date"]         = (today + timedelta(weeks=3)).isoformat()
    return scenario


# ── Port-constraint lookup (mirrors db/init_db.py seed — used when DB is unavailable)
PORT_CONSTRAINTS: Dict[str, Dict[str, Any]] = {
    "Paradip": {
        "max_draft_m": 16.5, "max_dwt_tonnes": 180_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 35_000,
        "laytime_allowed_days": 4.0,
        "demurrage_rate_usd_day": 20_000,
    },
    "Dhamra": {
        "max_draft_m": 18.4, "max_dwt_tonnes": 200_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 40_000,
        "laytime_allowed_days": 5.0,
        "demurrage_rate_usd_day": 22_000,
    },
    "Vizag": {
        "max_draft_m": 17.0, "max_dwt_tonnes": 180_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 30_000,
        "laytime_allowed_days": 4.5,
        "demurrage_rate_usd_day": 18_000,
    },
    "Gangavaram": {
        "max_draft_m": 17.0, "max_dwt_tonnes": 180_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 28_000,
        "laytime_allowed_days": 4.0,
        "demurrage_rate_usd_day": 18_000,
    },
    "Gopalpur": {
        "max_draft_m": 12.0, "max_dwt_tonnes": 60_000,
        "max_vessel_class": "Supramax",
        "cargo_handling_rate_tpd": 15_000,
        "laytime_allowed_days": 3.5,
        "demurrage_rate_usd_day": 12_000,
    },
    "Sagar-Sandheads": {
        "max_draft_m": 9.0, "max_dwt_tonnes": 30_000,
        "max_vessel_class": "Handysize",
        "cargo_handling_rate_tpd": 8_000,
        "laytime_allowed_days": 2.0,
        "demurrage_rate_usd_day": 8_000,
    },
    "Haldia": {
        "max_draft_m": 8.5, "max_dwt_tonnes": 25_000,
        "max_vessel_class": "Handysize",
        "cargo_handling_rate_tpd": 10_000,
        "laytime_allowed_days": 3.0,
        "demurrage_rate_usd_day": 10_000,
    },
}

# ── Vessel class capabilities ─────────────────────────────────────────────────
VESSEL_SPECS: Dict[str, Dict[str, Any]] = {
    "Handysize": {
        "typical_dwt":   28_000, "max_dwt":   40_000,
        "min_lot":       15_000, "max_lot":   38_000,
        "laden_draft_m": 8.5,   "beam_m": 23,
        "daily_cost_usd": 8_500,
    },
    "Supramax": {
        "typical_dwt":   55_000, "max_dwt":   65_000,
        "min_lot":       35_000, "max_lot":   60_000,
        "laden_draft_m": 11.5,  "beam_m": 32,
        "daily_cost_usd": 12_000,
    },
    "Panamax": {
        "typical_dwt":   75_000, "max_dwt":   85_000,
        "min_lot":       55_000, "max_lot":   80_000,
        "laden_draft_m": 13.5,  "beam_m": 32,
        "daily_cost_usd": 16_500,
    },
    "Capesize": {
        "typical_dwt":  170_000, "max_dwt":  210_000,
        "min_lot":      100_000, "max_lot":  180_000,
        "laden_draft_m": 17.5,  "beam_m": 45,
        "daily_cost_usd": 28_000,
    },
}

# ── Origin route parameters ────────────────────────────────────────────────────
ROUTE_PARAMS: Dict[str, Dict[str, Any]] = {
    "Australia_Paradip":      {"dist_nm": 4800, "sea_days": 15.4, "sanction_flag": False},
    "Australia_Dhamra":       {"dist_nm": 4900, "sea_days": 15.8, "sanction_flag": False},
    "Australia_Vizag":        {"dist_nm": 4750, "sea_days": 15.2, "sanction_flag": False},
    "Indonesia_Paradip":      {"dist_nm": 1800, "sea_days": 5.8,  "sanction_flag": False},
    "USA_Paradip":            {"dist_nm": 12000,"sea_days": 38.5, "sanction_flag": False},
    "Mozambique_Paradip":     {"dist_nm": 5200, "sea_days": 16.7, "sanction_flag": False},
    "Russia_Paradip":         {"dist_nm": 6200, "sea_days": 19.9, "sanction_flag": True},
}


def get_port_constraint(port_name: str) -> Dict[str, Any]:
    """Get port constraint dict (fallback to in-memory if DB unavailable)."""
    return PORT_CONSTRAINTS.get(port_name, PORT_CONSTRAINTS["Paradip"])


def is_vessel_feasible(vessel_class: str, port_name: str) -> bool:
    """Check if vessel class can berth at the given port."""
    order = ["Handysize", "Supramax", "Panamax", "Capesize"]
    constraint = get_port_constraint(port_name)
    max_class   = constraint.get("max_vessel_class", "Panamax")
    return order.index(vessel_class) <= order.index(max_class)
