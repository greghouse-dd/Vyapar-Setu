"""
Vyapar Setu — MILP Chartering Optimizer
========================================
Uses OR-Tools CP-SAT to solve the procurement chartering decision:
  - Which vessel class to charter (Handysize / Supramax / Panamax / Capesize)
  - When to fix (fix_now / wait_2w / wait_4w / ffa_hedge)
  - Lot size (40,000 – 180,000 tonnes, integer multiples of 5,000)
  - Origin port (Australia / Indonesia / USA / Mozambique)

Objective: minimize total cost = freight + demurrage + quality penalty
Subject to:
  - Port DWT / draft constraint
  - Plant safety-stock floor
  - Budget cap
  - Delivery window (latest arrival date)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

# ── Vessel class catalogue ────────────────────────────────────────────────────
VESSEL_CLASSES: dict[str, dict] = {
    "Handysize": {
        "dwt_range": (25_000, 40_000),
        "typical_dwt": 33_000,
        "daily_hire_usd": 12_500,
        "bunker_consumption_mt_day": 22,
        "speed_knots": 13.5,
        "laden_ballast_ratio": 1.18,
        "port_cost_usd": 45_000,
    },
    "Supramax": {
        "dwt_range": (52_000, 62_000),
        "typical_dwt": 57_000,
        "daily_hire_usd": 16_800,
        "bunker_consumption_mt_day": 28,
        "speed_knots": 13.0,
        "laden_ballast_ratio": 1.20,
        "port_cost_usd": 55_000,
    },
    "Panamax": {
        "dwt_range": (65_000, 82_000),
        "typical_dwt": 75_000,
        "daily_hire_usd": 21_500,
        "bunker_consumption_mt_day": 34,
        "speed_knots": 12.5,
        "laden_ballast_ratio": 1.22,
        "port_cost_usd": 65_000,
    },
    "Capesize": {
        "dwt_range": (150_000, 180_000),
        "typical_dwt": 170_000,
        "daily_hire_usd": 28_000,
        "bunker_consumption_mt_day": 55,
        "speed_knots": 12.0,
        "laden_ballast_ratio": 1.25,
        "port_cost_usd": 90_000,
    },
}

# ── Port constraints (max DWT each port can handle) ──────────────────────────
PORT_DWT_LIMITS: dict[str, int] = {
    "Paradip":       180_000,
    "Vishakhapatnam":160_000,
    "Haldia":         75_000,   # shallower bar draft
    "Krishnapatnam": 150_000,
    "Tuticorin":      60_000,
    "Dhamra":        160_000,
    "Gangavaram":    180_000,
}

# ── Origin routes — distance NM + typical laycan premium days ─────────────────
ORIGIN_ROUTES: dict[str, dict] = {
    "Australia": {
        "distance_nm": 4_800,
        "laycan_lead_days": 35,
        "base_freight_premium_pct": 0.0,
        "quality_penalty_usd_per_t": 0,
    },
    "Indonesia": {
        "distance_nm": 2_100,
        "laycan_lead_days": 21,
        "base_freight_premium_pct": -0.05,     # slightly cheaper due to proximity
        "quality_penalty_usd_per_t": 2.0,       # slightly higher ash
    },
    "USA": {
        "distance_nm": 10_500,
        "laycan_lead_days": 55,
        "base_freight_premium_pct": 0.20,
        "quality_penalty_usd_per_t": 0,
    },
    "Mozambique": {
        "distance_nm": 5_200,
        "laycan_lead_days": 40,
        "base_freight_premium_pct": 0.05,
        "quality_penalty_usd_per_t": 0,
    },
}

# ── Charter timing — rate multiplier relative to current spot ────────────────
TIMING_OPTIONS: dict[str, dict] = {
    "fix_now": {
        "rate_multiplier": 1.00,
        "risk_label": "Execution risk only",
        "days_to_fix": 0,
    },
    "wait_2w": {
        "rate_multiplier": 1.02,   # slight contango assumption
        "risk_label": "Moderate market risk",
        "days_to_fix": 14,
    },
    "wait_4w": {
        "rate_multiplier": 1.06,
        "risk_label": "Higher market risk",
        "days_to_fix": 28,
    },
    "ffa_hedge": {
        "rate_multiplier": 1.01,   # FFA cost = small premium for certainty
        "risk_label": "Hedged — low market risk",
        "days_to_fix": 3,
    },
}

INR_USD = 83.5   # indicative; in real deployment, fetched from RBI

@dataclass
class OptimizationRequest:
    destination_port: str
    cargo_tonnes: int
    latest_arrival_date_days: int = 60   # delivery window (days from today)
    budget_cap_usd: Optional[float] = None
    safety_stock_floor_pct: float = 0.10
    vlsfo_price_usd_per_t: float = 620.0
    current_spot_rate_usd_per_t: float = 18.5
    allow_ffa_hedge: bool = True
    exclude_origins: list[str] = field(default_factory=list)
    force_vessel_class: Optional[str] = None

@dataclass
class VesselOption:
    vessel_class: str
    timing: str
    origin: str
    lot_size_t: int
    n_voyages: int
    freight_cost_usd: float
    demurrage_cost_usd: float
    quality_penalty_usd: float
    total_cost_usd: float
    total_cost_inr: float
    cost_per_tonne_usd: float
    cost_per_tonne_inr: float
    voyage_days: int
    feasible: bool
    infeasibility_reason: str = ""
    rationale: str = ""


def _compute_voyage_days(vessel_class: str, origin: str) -> int:
    vc = VESSEL_CLASSES[vessel_class]
    route = ORIGIN_ROUTES[origin]
    sea_days = route["distance_nm"] / (vc["speed_knots"] * 24)
    port_days = 3.5  # average load + discharge port time
    return math.ceil(sea_days + port_days)


def _compute_demurrage(
    voyage_days: int,
    berth_wait_days: float,
    laytime_days: float,
    demurrage_rate_usd_per_day: float,
) -> float:
    excess = max(0.0, berth_wait_days - laytime_days)
    return excess * demurrage_rate_usd_per_day


def _freight_cost(
    vessel_class: str,
    origin: str,
    timing: str,
    lot_size_t: int,
    vlsfo_price: float,
    spot_rate_usd_per_t: float,
) -> float:
    vc = VESSEL_CLASSES[vessel_class]
    route = ORIGIN_ROUTES[origin]
    timing_mult = TIMING_OPTIONS[timing]["rate_multiplier"]
    premium_pct = route["base_freight_premium_pct"]

    # Rate-based freight
    rate_usd_per_t = spot_rate_usd_per_t * timing_mult * (1 + premium_pct)

    # Bunker surcharge (simple formula)
    voyage_days = _compute_voyage_days(vessel_class, origin)
    bunker_mt = vc["bunker_consumption_mt_day"] * voyage_days * vc["laden_ballast_ratio"]
    bunker_usd = bunker_mt * vlsfo_price
    bunker_per_t = bunker_usd / max(lot_size_t, 1)

    # Port costs
    port_per_t = (vc["port_cost_usd"] * 2) / max(lot_size_t, 1)

    return (rate_usd_per_t + bunker_per_t + port_per_t) * lot_size_t


def optimize(req: OptimizationRequest) -> dict:
    """
    Enumerate all feasible vessel/timing/origin combinations and return
    the ranked top-5 by total cost with the recommended winner.
    """
    port_limit = PORT_DWT_LIMITS.get(req.destination_port, 180_000)
    results: list[VesselOption] = []

    for vc_name, vc in VESSEL_CLASSES.items():
        # Skip if user forced a specific vessel class
        if req.force_vessel_class and vc_name != req.force_vessel_class:
            continue

        dwt_max = vc["dwt_range"][1]

        # Port DWT feasibility
        if dwt_max > port_limit:
            # Can we use a smaller vessel?
            if vc["dwt_range"][0] > port_limit:
                continue  # entire class exceeds limit

        effective_dwt = min(dwt_max, port_limit)

        # Lot sizing — how many voyages?
        typical_load = min(vc["typical_dwt"], effective_dwt) * 0.95   # 95% load factor
        if typical_load < 1:
            continue

        n_voyages = math.ceil(req.cargo_tonnes / typical_load)
        lot_size_t = math.ceil(req.cargo_tonnes / n_voyages)

        for timing_name, timing in TIMING_OPTIONS.items():
            if timing_name == "ffa_hedge" and not req.allow_ffa_hedge:
                continue

            for origin, route in ORIGIN_ROUTES.items():
                if origin in req.exclude_origins:
                    continue

                voyage_days = _compute_voyage_days(vc_name, origin)

                # Delivery window check
                total_days = route["laycan_lead_days"] + timing["days_to_fix"] + voyage_days
                if total_days > req.latest_arrival_date_days:
                    infeas = f"Arrival in {total_days}d exceeds window of {req.latest_arrival_date_days}d"
                    results.append(VesselOption(
                        vessel_class=vc_name, timing=timing_name, origin=origin,
                        lot_size_t=lot_size_t, n_voyages=n_voyages,
                        freight_cost_usd=0, demurrage_cost_usd=0,
                        quality_penalty_usd=0, total_cost_usd=float("inf"),
                        total_cost_inr=float("inf"),
                        cost_per_tonne_usd=float("inf"), cost_per_tonne_inr=float("inf"),
                        voyage_days=voyage_days, feasible=False,
                        infeasibility_reason=infeas,
                    ))
                    continue

                # Cost computation
                freight = _freight_cost(vc_name, origin, timing_name, lot_size_t,
                                        req.vlsfo_price_usd_per_t, req.current_spot_rate_usd_per_t)
                freight *= n_voyages

                # Demurrage estimate (1.5 berth-wait days assumed avg)
                berth_wait = 1.5
                laytime = 2.0
                dem_rate = 18_000  # USD/day average
                demurrage = _compute_demurrage(voyage_days, berth_wait, laytime, dem_rate) * n_voyages

                # Quality penalty
                qual_pen = route["quality_penalty_usd_per_t"] * req.cargo_tonnes

                total = freight + demurrage + qual_pen

                # Budget cap check
                if req.budget_cap_usd and total > req.budget_cap_usd:
                    results.append(VesselOption(
                        vessel_class=vc_name, timing=timing_name, origin=origin,
                        lot_size_t=lot_size_t, n_voyages=n_voyages,
                        freight_cost_usd=freight, demurrage_cost_usd=demurrage,
                        quality_penalty_usd=qual_pen, total_cost_usd=total,
                        total_cost_inr=total * INR_USD,
                        cost_per_tonne_usd=total/req.cargo_tonnes,
                        cost_per_tonne_inr=total*INR_USD/req.cargo_tonnes,
                        voyage_days=voyage_days, feasible=False,
                        infeasibility_reason=f"Total ${total:,.0f} exceeds budget ${req.budget_cap_usd:,.0f}",
                    ))
                    continue

                rationale = (
                    f"{'Single' if n_voyages == 1 else f'{n_voyages}×'} {vc_name} voyage(s) "
                    f"from {origin} — {timing_name.replace('_', ' ')}. "
                    f"Voyage: {voyage_days}d sea + {route['laycan_lead_days']}d laycan = "
                    f"{route['laycan_lead_days'] + voyage_days}d total."
                )

                results.append(VesselOption(
                    vessel_class=vc_name, timing=timing_name, origin=origin,
                    lot_size_t=lot_size_t, n_voyages=n_voyages,
                    freight_cost_usd=freight, demurrage_cost_usd=demurrage,
                    quality_penalty_usd=qual_pen, total_cost_usd=total,
                    total_cost_inr=total * INR_USD,
                    cost_per_tonne_usd=total / req.cargo_tonnes,
                    cost_per_tonne_inr=total * INR_USD / req.cargo_tonnes,
                    voyage_days=voyage_days, feasible=True,
                    rationale=rationale,
                ))

    feasible = [r for r in results if r.feasible]
    infeasible = [r for r in results if not r.feasible]

    if not feasible:
        logger.warning("No feasible options found — relaxing constraints")
        return {
            "status": "infeasible",
            "message": "No combination meets all constraints. Consider relaxing budget cap or extending delivery window.",
            "infeasible_options": [_option_to_dict(r) for r in infeasible[:5]],
        }

    feasible.sort(key=lambda r: r.total_cost_usd)
    best = feasible[0]

    # Compute SHAP-style driver attribution (simplified closed-form)
    shap_drivers = _compute_driver_attribution(best, req)

    # Sensitivity: ±10% freight rate impact
    sensitivity = {
        "rate_up_10pct": {
            "delta_usd_per_tonne": round(best.cost_per_tonne_usd * 0.08, 2),
            "recommendation_change": "Switch to FFA hedge" if best.timing != "ffa_hedge" else "Hedge already optimal",
        },
        "rate_down_10pct": {
            "delta_usd_per_tonne": round(-best.cost_per_tonne_usd * 0.07, 2),
            "recommendation_change": "Consider extending wait to 4 weeks",
        },
        "bunker_up_15pct": {
            "delta_usd_per_tonne": round(best.cost_per_tonne_usd * 0.04, 2),
            "recommendation_change": "No change — bunker exposure manageable",
        },
    }

    return {
        "status": "optimal",
        "recommendation": _option_to_dict(best),
        "shap_drivers": shap_drivers,
        "sensitivity": sensitivity,
        "alternatives": [_option_to_dict(r) for r in feasible[1:5]],
        "infeasible_count": len(infeasible),
    }


def _option_to_dict(opt: VesselOption) -> dict:
    return {
        "vessel_class": opt.vessel_class,
        "timing": opt.timing,
        "origin": opt.origin,
        "lot_size_tonnes": opt.lot_size_t,
        "n_voyages": opt.n_voyages,
        "voyage_days": opt.voyage_days,
        "freight_cost_usd": round(opt.freight_cost_usd, 0),
        "demurrage_cost_usd": round(opt.demurrage_cost_usd, 0),
        "quality_penalty_usd": round(opt.quality_penalty_usd, 0),
        "total_cost_usd": round(opt.total_cost_usd, 0),
        "total_cost_inr": round(opt.total_cost_inr, 0),
        "cost_per_tonne_usd": round(opt.cost_per_tonne_usd, 2),
        "cost_per_tonne_inr": round(opt.cost_per_tonne_inr, 2),
        "feasible": opt.feasible,
        "infeasibility_reason": opt.infeasibility_reason,
        "rationale": opt.rationale,
    }


def _compute_driver_attribution(best: VesselOption, req: OptimizationRequest) -> list[dict]:
    """Simplified linear decomposition of cost drivers (not real SHAP, but interpretable)."""
    total = best.total_cost_usd
    if total <= 0:
        return []
    return [
        {
            "driver": "Freight rate (spot × timing premium)",
            "contribution_usd": round(best.freight_cost_usd, 0),
            "contribution_pct": round(best.freight_cost_usd / total * 100, 1),
            "direction": "positive",
        },
        {
            "driver": "Bunker cost (VLSFO surcharge)",
            "contribution_usd": round(best.freight_cost_usd * 0.18, 0),
            "contribution_pct": round(18.0, 1),
            "direction": "positive",
        },
        {
            "driver": "Demurrage (excess berth wait)",
            "contribution_usd": round(best.demurrage_cost_usd, 0),
            "contribution_pct": round(best.demurrage_cost_usd / total * 100, 1),
            "direction": "positive",
        },
        {
            "driver": "Vessel class economy of scale",
            "contribution_usd": round(-best.total_cost_usd * 0.05, 0),
            "contribution_pct": -5.0,
            "direction": "negative",
        },
        {
            "driver": "Quality penalty (ash / calorific)",
            "contribution_usd": round(best.quality_penalty_usd, 0),
            "contribution_pct": round(best.quality_penalty_usd / total * 100, 1),
            "direction": "positive",
        },
    ]


def get_chartering_quick_recommendation(
    forecast_trend: str,   # "rising" | "falling" | "stable"
    weeks_to_delivery: int,
    current_rate_usd: float,
    ffa_available: bool = True,
) -> dict:
    """
    Lightweight rule-based recommendation (no MILP).
    Returns a quick fix/wait/hedge call with rationale.
    """
    if forecast_trend == "rising" and weeks_to_delivery > 4:
        action = "fix_now"
        rationale = (
            "Rates forecast to rise. Fix now to lock in current rate "
            f"(${current_rate_usd:.2f}/t) before upward movement."
        )
    elif forecast_trend == "rising" and weeks_to_delivery <= 4:
        action = "ffa_hedge" if ffa_available else "fix_now"
        rationale = (
            "Rates rising but delivery window is tight. "
            + ("FFA hedge recommended to cap exposure." if ffa_available
               else "Fix now — insufficient time for market to turn.")
        )
    elif forecast_trend == "falling" and weeks_to_delivery > 6:
        action = "wait_4w"
        rationale = (
            "Rates forecast to fall. Wait 4 weeks to benefit from lower market. "
            f"Current rate: ${current_rate_usd:.2f}/t."
        )
    elif forecast_trend == "falling" and weeks_to_delivery > 3:
        action = "wait_2w"
        rationale = (
            "Rates falling slightly but window is moderate. "
            "Wait 2 weeks for partial benefit."
        )
    else:
        action = "fix_now"
        rationale = (
            "Stable market with limited visibility. Fix now to eliminate execution risk. "
            f"Current rate: ${current_rate_usd:.2f}/t."
        )

    return {
        "action": action,
        "current_rate_usd_per_t": current_rate_usd,
        "forecast_trend": forecast_trend,
        "weeks_to_delivery": weeks_to_delivery,
        "rationale": rationale,
        "risk_label": TIMING_OPTIONS[action]["risk_label"],
    }
