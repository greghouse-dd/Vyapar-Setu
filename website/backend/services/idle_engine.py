"""
Vyapar Setu — Idle Fleet & Deadheading Advisor
================================================
After a vessel discharges cargo at an Indian port, this advisor recommends
the optimal next action:
  1. Ballast reposition → port with a profitable next cargo
  2. Backhaul → export cargo (iron ore, limestone, granite) heading away
  3. Relet → sublet the vessel to another operator at current TCE
  4. Idle wait → if rates expected to rise within 2–3 weeks

Algorithm:
  - Fetch 4-week freight forecast for all 7 named ports (from scenario_service)
  - Compute ballast voyage cost to each port
  - Estimate expected earnings at each port
  - Compute net value = expected earnings − ballast cost
  - Check backhaul routes from a static route table
  - Rank all strategies by net value
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from loguru import logger

# ── Port distance matrix (NM from each port to each port) ────────────────────
# Simplified symmetric matrix for Indian coastal ports
PORT_DISTANCES_NM: dict[tuple[str, str], int] = {
    ("Paradip", "Vishakhapatnam"):   440,
    ("Paradip", "Haldia"):            200,
    ("Paradip", "Krishnapatnam"):    680,
    ("Paradip", "Tuticorin"):       1_580,
    ("Paradip", "Dhamra"):            120,
    ("Paradip", "Gangavaram"):        620,
    ("Vishakhapatnam", "Haldia"):    600,
    ("Vishakhapatnam", "Krishnapatnam"): 240,
    ("Vishakhapatnam", "Tuticorin"):  1_140,
    ("Vishakhapatnam", "Dhamra"):    520,
    ("Vishakhapatnam", "Gangavaram"):  80,
    ("Haldia", "Krishnapatnam"):     840,
    ("Haldia", "Tuticorin"):       1_760,
    ("Haldia", "Dhamra"):            280,
    ("Haldia", "Gangavaram"):        760,
    ("Krishnapatnam", "Tuticorin"):   900,
    ("Krishnapatnam", "Dhamra"):     760,
    ("Krishnapatnam", "Gangavaram"): 160,
    ("Tuticorin", "Dhamra"):       1_660,
    ("Tuticorin", "Gangavaram"):   1_060,
    ("Dhamra", "Gangavaram"):         700,
}

def _port_distance(p1: str, p2: str) -> int:
    key = (p1, p2) if (p1, p2) in PORT_DISTANCES_NM else (p2, p1)
    return PORT_DISTANCES_NM.get(key, 1_000)   # default if not found


# ── Vessel class specs ────────────────────────────────────────────────────────
VESSEL_SPECS: dict[str, dict] = {
    "Handysize": {
        "ballast_speed_knots": 14.0,
        "ballast_bunker_mt_day": 18.0,
        "typical_tce_usd_day": 10_000,
        "typical_cargo_t": 33_000,
    },
    "Supramax": {
        "ballast_speed_knots": 13.5,
        "ballast_bunker_mt_day": 24.0,
        "typical_tce_usd_day": 14_000,
        "typical_cargo_t": 57_000,
    },
    "Panamax": {
        "ballast_speed_knots": 13.0,
        "ballast_bunker_mt_day": 30.0,
        "typical_tce_usd_day": 18_000,
        "typical_cargo_t": 75_000,
    },
    "Capesize": {
        "ballast_speed_knots": 12.5,
        "ballast_bunker_mt_day": 48.0,
        "typical_tce_usd_day": 24_000,
        "typical_cargo_t": 170_000,
    },
}

# ── Static backhaul routes (Indian export legs) ───────────────────────────────
BACKHAUL_ROUTES: list[dict] = [
    {
        "load_port": "Paradip",
        "discharge_port": "Qingdao, China",
        "commodity": "Iron Ore",
        "distance_nm": 3_200,
        "freight_usd_per_t": 8.5,
        "typical_lot_t": 65_000,
        "vessel_classes": ["Panamax", "Capesize"],
    },
    {
        "load_port": "Vishakhapatnam",
        "discharge_port": "Qingdao, China",
        "commodity": "Iron Ore",
        "distance_nm": 3_100,
        "freight_usd_per_t": 8.8,
        "typical_lot_t": 65_000,
        "vessel_classes": ["Panamax", "Capesize"],
    },
    {
        "load_port": "Paradip",
        "discharge_port": "Richards Bay, SA",
        "commodity": "Limestone",
        "distance_nm": 5_800,
        "freight_usd_per_t": 12.0,
        "typical_lot_t": 45_000,
        "vessel_classes": ["Supramax", "Panamax"],
    },
    {
        "load_port": "Tuticorin",
        "discharge_port": "Singapore",
        "commodity": "Granite",
        "distance_nm": 1_600,
        "freight_usd_per_t": 6.5,
        "typical_lot_t": 30_000,
        "vessel_classes": ["Handysize", "Supramax"],
    },
    {
        "load_port": "Haldia",
        "discharge_port": "Chittagong, Bangladesh",
        "commodity": "Rice/Grain",
        "distance_nm": 420,
        "freight_usd_per_t": 14.0,
        "typical_lot_t": 25_000,
        "vessel_classes": ["Handysize"],
    },
]

VLSFO_DEFAULT_USD = 620.0
INR_USD = 83.5


@dataclass
class IdleAdvisorRequest:
    vessel_class: str
    current_port: str
    dwt: int
    last_discharge_date_days_ago: int = 0    # 0 = just discharged
    idle_cost_per_day_usd: float = 2_500     # crew + P&I + maintenance
    vlsfo_price_usd: float = VLSFO_DEFAULT_USD
    forecast_horizon_weeks: int = 4
    current_tce_estimate_usd_day: Optional[float] = None
    # Freight rate forecasts per port for the next N weeks (usd/tonne)
    port_rate_forecasts: Optional[dict[str, float]] = None


@dataclass
class StrategyOption:
    strategy: str     # ballast_reposition | backhaul | relet | idle
    destination: str
    commodity: str
    gross_revenue_usd: float
    ballast_cost_usd: float
    idle_wait_cost_usd: float
    net_value_usd: float
    net_value_inr: float
    voyage_days: int
    confidence: str    # high | medium | low
    p10_usd: float
    p90_usd: float
    rationale: str


def _ballast_cost(vessel_class: str, distance_nm: int, vlsfo_price: float) -> float:
    specs = VESSEL_SPECS[vessel_class]
    days = distance_nm / (specs["ballast_speed_knots"] * 24)
    bunker_cost = specs["ballast_bunker_mt_day"] * days * vlsfo_price
    return round(bunker_cost + (days * 800), 2)   # + port dues


def _default_rate_forecast(port: str, vessel_class: str) -> float:
    """Fallback rate per tonne if no forecast provided."""
    base = VESSEL_SPECS[vessel_class]["typical_tce_usd_day"]
    # Convert TCE to per-tonne using typical voyage length
    cargo_t = VESSEL_SPECS[vessel_class]["typical_cargo_t"]
    voyage_days = 30   # avg
    return round(base * voyage_days / max(cargo_t, 1), 2)


def advise(req: IdleAdvisorRequest) -> dict:
    """
    Returns ranked strategy list with the top recommendation.
    """
    specs = VESSEL_SPECS.get(req.vessel_class)
    if not specs:
        return {"error": f"Unknown vessel class: {req.vessel_class}"}

    options: list[StrategyOption] = []
    all_ports = [
        "Paradip", "Vishakhapatnam", "Haldia",
        "Krishnapatnam", "Tuticorin", "Dhamra", "Gangavaram",
    ]
    other_ports = [p for p in all_ports if p != req.current_port]

    # ── Strategy 1: Ballast Reposition ───────────────────────────────────────
    for port in other_ports:
        distance = _port_distance(req.current_port, port)
        ballast_cost = _ballast_cost(req.vessel_class, distance, req.vlsfo_price_usd)

        # Get rate forecast
        if req.port_rate_forecasts and port in req.port_rate_forecasts:
            rate = req.port_rate_forecasts[port]
        else:
            rate = _default_rate_forecast(port, req.vessel_class)

        cargo_t = min(specs["typical_cargo_t"], req.dwt * 0.95)
        gross_rev = rate * cargo_t
        idle_wait = req.idle_cost_per_day_usd * 3   # avg 3 day wait at new port
        net = gross_rev - ballast_cost - idle_wait

        voyage_d = math.ceil(distance / (specs["ballast_speed_knots"] * 24))
        p10 = net * 0.80
        p90 = net * 1.25

        options.append(StrategyOption(
            strategy="ballast_reposition",
            destination=port,
            commodity="Import coal / bulk",
            gross_revenue_usd=round(gross_rev, 0),
            ballast_cost_usd=round(ballast_cost, 0),
            idle_wait_cost_usd=round(idle_wait, 0),
            net_value_usd=round(net, 0),
            net_value_inr=round(net * INR_USD, 0),
            voyage_days=voyage_d,
            confidence="medium",
            p10_usd=round(p10, 0),
            p90_usd=round(p90, 0),
            rationale=(
                f"Ballast {distance} NM to {port} in {voyage_d}d. "
                f"Ballast cost: ${ballast_cost:,.0f}. "
                f"Expected revenue: ${gross_rev:,.0f} ({rate:.2f}/t × {cargo_t:,.0f}t). "
                f"Net: ${net:,.0f}."
            ),
        ))

    # ── Strategy 2: Backhaul ─────────────────────────────────────────────────
    for bh in BACKHAUL_ROUTES:
        if bh["load_port"] != req.current_port:
            continue
        if req.vessel_class not in bh["vessel_classes"]:
            continue

        lot_t = min(bh["typical_lot_t"], req.dwt * 0.95)
        gross_rev = bh["freight_usd_per_t"] * lot_t
        ballast_cost = 0   # already at load port
        load_wait = req.idle_cost_per_day_usd * 5   # avg load time
        net = gross_rev - load_wait

        p10 = net * 0.75
        p90 = net * 1.30

        options.append(StrategyOption(
            strategy="backhaul",
            destination=bh["discharge_port"],
            commodity=bh["commodity"],
            gross_revenue_usd=round(gross_rev, 0),
            ballast_cost_usd=0,
            idle_wait_cost_usd=round(load_wait, 0),
            net_value_usd=round(net, 0),
            net_value_inr=round(net * INR_USD, 0),
            voyage_days=math.ceil(bh["distance_nm"] / (specs["ballast_speed_knots"] * 24)),
            confidence="high",
            p10_usd=round(p10, 0),
            p90_usd=round(p90, 0),
            rationale=(
                f"Backhaul {bh['commodity']} from {bh['load_port']} to {bh['discharge_port']}. "
                f"No ballast leg required — zero repositioning cost. "
                f"Revenue: ${gross_rev:,.0f} ({bh['freight_usd_per_t']:.2f}/t × {lot_t:,.0f}t)."
            ),
        ))

    # ── Strategy 3: Relet ────────────────────────────────────────────────────
    tce = req.current_tce_estimate_usd_day or specs["typical_tce_usd_day"] * 0.85
    relet_days = req.forecast_horizon_weeks * 7
    relet_rev = tce * relet_days
    idle_cost_total = req.idle_cost_per_day_usd * relet_days
    relet_net = relet_rev - idle_cost_total

    options.append(StrategyOption(
        strategy="relet",
        destination="Open market (spot)",
        commodity="Any",
        gross_revenue_usd=round(relet_rev, 0),
        ballast_cost_usd=0,
        idle_wait_cost_usd=round(idle_cost_total * 0.1, 0),
        net_value_usd=round(relet_net, 0),
        net_value_inr=round(relet_net * INR_USD, 0),
        voyage_days=relet_days,
        confidence="medium",
        p10_usd=round(relet_net * 0.85, 0),
        p90_usd=round(relet_net * 1.15, 0),
        rationale=(
            f"Relet vessel on spot market at estimated TCE ${tce:,.0f}/day "
            f"for {relet_days} days = ${relet_rev:,.0f} gross. "
            "Suitable when own fleet cannot absorb the voyage immediately."
        ),
    ))

    # ── Strategy 4: Idle Wait ────────────────────────────────────────────────
    wait_days = req.forecast_horizon_weeks * 7
    idle_total_cost = req.idle_cost_per_day_usd * wait_days

    options.append(StrategyOption(
        strategy="idle",
        destination=req.current_port,
        commodity="None",
        gross_revenue_usd=0,
        ballast_cost_usd=0,
        idle_wait_cost_usd=round(idle_total_cost, 0),
        net_value_usd=-round(idle_total_cost, 0),
        net_value_inr=-round(idle_total_cost * INR_USD, 0),
        voyage_days=wait_days,
        confidence="low",
        p10_usd=-round(idle_total_cost * 1.20, 0),
        p90_usd=-round(idle_total_cost * 0.80, 0),
        rationale=(
            f"Idle at {req.current_port} for {wait_days}d costs "
            f"${idle_total_cost:,.0f} in fixed operating expenses. "
            "Only advisable if market expected to spike significantly within the window."
        ),
    ))

    # ── Rank by net value ─────────────────────────────────────────────────────
    options.sort(key=lambda x: x.net_value_usd, reverse=True)
    best = options[0]

    return {
        "recommended_strategy": best.strategy,
        "recommended_destination": best.destination,
        "net_value_usd": best.net_value_usd,
        "net_value_inr": best.net_value_inr,
        "rationale": best.rationale,
        "confidence": best.confidence,
        "p10_usd": best.p10_usd,
        "p90_usd": best.p90_usd,
        "all_strategies": [
            {
                "strategy": o.strategy,
                "destination": o.destination,
                "commodity": o.commodity,
                "gross_revenue_usd": o.gross_revenue_usd,
                "ballast_cost_usd": o.ballast_cost_usd,
                "idle_wait_cost_usd": o.idle_wait_cost_usd,
                "net_value_usd": o.net_value_usd,
                "net_value_inr": o.net_value_inr,
                "voyage_days": o.voyage_days,
                "confidence": o.confidence,
                "p10_usd": o.p10_usd,
                "p90_usd": o.p90_usd,
                "rationale": o.rationale,
            }
            for o in options
        ],
    }
