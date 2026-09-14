"""
Vyapar Setu — Cross-PSU Cargo Pooling Engine
=============================================
Evaluates whether two PSU demand lots (e.g., SAIL + RINL) are better
served by separate vessels or a single pooled voyage on a larger vessel.

Algorithm:
  1. Compute separate-vessel cost (each lot on its own optimal vessel class).
  2. Compute pooled cost (single larger vessel, pro-rata cost split).
  3. Feasibility check: combined tonnes vs. destination port DWT limits.
  4. Return recommendation with per-PSU and aggregate savings.

Endpoint input: two DemandLot objects + shared destination port.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

# ── Vessel cost model (simplified $/tonne base rates) ────────────────────────
# These are indicative rates for Australia→India (Panamax benchmark ≈ $18/t)
VESSEL_RATE_USD_PER_T: dict[str, float] = {
    "Handysize": 24.5,
    "Supramax":  21.0,
    "Panamax":   18.5,
    "Capesize":  14.2,   # economy of scale
}

VESSEL_MAX_CARGO_T: dict[str, int] = {
    "Handysize":  36_000,
    "Supramax":   58_000,
    "Panamax":    77_000,
    "Capesize":  170_000,
}

PORT_DWT_LIMITS: dict[str, int] = {
    "Paradip":        180_000,
    "Vishakhapatnam": 160_000,
    "Haldia":          75_000,
    "Krishnapatnam":  150_000,
    "Tuticorin":       60_000,
    "Dhamra":         160_000,
    "Gangavaram":     180_000,
}

INR_USD = 83.5


@dataclass
class DemandLot:
    psu_name: str                         # e.g., "SAIL", "RINL"
    cargo_tonnes: int
    destination_port: str
    commodity: str = "Coal"
    delivery_window_days: int = 60
    max_draft_m: Optional[float] = None   # if provided, overrides port table


@dataclass
class PoolingResult:
    recommendation: str                   # "pool" | "separate"
    feasible: bool
    infeasibility_notes: list[str]

    # Separate scenario
    lot_a_separate_vessel: str
    lot_b_separate_vessel: str
    lot_a_separate_cost_usd: float
    lot_b_separate_cost_usd: float
    total_separate_cost_usd: float

    # Pooled scenario
    pooled_vessel_class: str
    pooled_cost_usd: float
    lot_a_pooled_share_usd: float
    lot_b_pooled_share_usd: float

    # Savings
    saving_usd: float
    saving_inr: float
    saving_per_tonne_usd: float
    saving_per_tonne_inr: float
    saving_pct: float

    rationale: str
    caveats: list[str]


def _pick_vessel(cargo_t: int, port_dwt_limit: int) -> tuple[str, float]:
    """Pick the smallest feasible vessel class and return its cost."""
    for vc_name, max_t in sorted(VESSEL_MAX_CARGO_T.items(), key=lambda x: x[1]):
        if max_t >= cargo_t and max_t <= port_dwt_limit * 1.05:  # 5% slack for partial load
            rate = VESSEL_RATE_USD_PER_T[vc_name]
            return vc_name, rate * cargo_t
    # Fallback: Capesize even if over limit (flag as infeasible)
    return "Capesize", VESSEL_RATE_USD_PER_T["Capesize"] * cargo_t


def _port_limit(lot: DemandLot) -> int:
    if lot.max_draft_m:
        # Very rough draft→DWT mapping (generic)
        if lot.max_draft_m < 12.0:
            return 60_000
        elif lot.max_draft_m < 14.5:
            return 80_000
        elif lot.max_draft_m < 17.0:
            return 160_000
        else:
            return 180_000
    return PORT_DWT_LIMITS.get(lot.destination_port, 150_000)


def analyze(lot_a: DemandLot, lot_b: DemandLot) -> PoolingResult:
    """
    Main pooling analysis function.
    Returns a PoolingResult with full cost comparison and recommendation.
    """
    infeasibility_notes: list[str] = []
    caveats: list[str] = []

    port_limit_a = _port_limit(lot_a)
    port_limit_b = _port_limit(lot_b)

    # ── Separate scenario ────────────────────────────────────────────────────
    vc_a, cost_a = _pick_vessel(lot_a.cargo_tonnes, port_limit_a)
    vc_b, cost_b = _pick_vessel(lot_b.cargo_tonnes, port_limit_b)
    total_separate = cost_a + cost_b

    # ── Pooled scenario ──────────────────────────────────────────────────────
    combined_t = lot_a.cargo_tonnes + lot_b.cargo_tonnes
    # Pooled delivery: both go to whichever port has the higher draft limit
    # (in practice, the load is split at discharge; here we assume co-loading to
    # the same destination — flag mismatch as a caveat)
    if lot_a.destination_port != lot_b.destination_port:
        caveats.append(
            f"Lots have different destination ports ({lot_a.destination_port} vs "
            f"{lot_b.destination_port}). Pooled scenario assumes transshipment or "
            f"same-port delivery via lighterage; additional cost not modelled."
        )

    effective_port_limit = min(port_limit_a, port_limit_b)
    vc_pooled, pooled_cost = _pick_vessel(combined_t, effective_port_limit)

    # Pro-rata split by tonnage
    share_a = lot_a.cargo_tonnes / combined_t
    share_b = lot_b.cargo_tonnes / combined_t
    cost_a_pooled = pooled_cost * share_a
    cost_b_pooled = pooled_cost * share_b

    saving_usd = total_separate - pooled_cost
    saving_inr = saving_usd * INR_USD
    saving_per_t = saving_usd / combined_t
    saving_pct = saving_usd / total_separate * 100 if total_separate > 0 else 0

    # ── Feasibility checks ──────────────────────────────────────────────────
    feasible = True
    if combined_t > effective_port_limit:
        infeasibility_notes.append(
            f"Combined cargo ({combined_t:,} t) exceeds port DWT limit "
            f"({effective_port_limit:,} t at {lot_a.destination_port}). "
            "Pooling physically infeasible without lighterage."
        )
        feasible = False

    if vc_pooled == "Capesize" and effective_port_limit < 160_000:
        infeasibility_notes.append(
            f"Capesize vessel ({combined_t:,} t) required for pooling but "
            f"port limit is only {effective_port_limit:,} t. Use Dhamra or Gangavaram instead."
        )
        feasible = False

    # Delivery window check
    if abs(lot_a.delivery_window_days - lot_b.delivery_window_days) > 14:
        caveats.append(
            "Delivery windows differ by more than 14 days. Pooling may cause one lot "
            "to arrive late. Consider adjusting procurement schedules."
        )

    # ── Recommendation ───────────────────────────────────────────────────────
    if not feasible:
        recommendation = "separate"
        rationale = (
            f"Pooling is physically infeasible for these lots at the destination port. "
            f"Recommended: {vc_a} for {lot_a.psu_name} ({lot_a.cargo_tonnes:,} t) "
            f"and {vc_b} for {lot_b.psu_name} ({lot_b.cargo_tonnes:,} t) separately. "
            f"Total cost: ${total_separate:,.0f}."
        )
    elif saving_usd > 0:
        recommendation = "pool"
        rationale = (
            f"Pooling {lot_a.psu_name} ({lot_a.cargo_tonnes:,} t) + "
            f"{lot_b.psu_name} ({lot_b.cargo_tonnes:,} t) onto a single {vc_pooled} "
            f"saves ${saving_usd:,.0f} (₹{saving_inr:,.0f}) vs. separate chartering. "
            f"Economy-of-scale: ${VESSEL_RATE_USD_PER_T[vc_pooled]:.2f}/t vs "
            f"${VESSEL_RATE_USD_PER_T[vc_a]:.2f}/t (sep-A) + "
            f"${VESSEL_RATE_USD_PER_T[vc_b]:.2f}/t (sep-B)."
        )
    else:
        recommendation = "separate"
        rationale = (
            f"No saving from pooling (combined total ${pooled_cost:,.0f} ≥ "
            f"separate total ${total_separate:,.0f}). Recommend separate charters."
        )

    return PoolingResult(
        recommendation=recommendation,
        feasible=feasible,
        infeasibility_notes=infeasibility_notes,
        lot_a_separate_vessel=vc_a,
        lot_b_separate_vessel=vc_b,
        lot_a_separate_cost_usd=cost_a,
        lot_b_separate_cost_usd=cost_b,
        total_separate_cost_usd=total_separate,
        pooled_vessel_class=vc_pooled,
        pooled_cost_usd=pooled_cost,
        lot_a_pooled_share_usd=cost_a_pooled,
        lot_b_pooled_share_usd=cost_b_pooled,
        saving_usd=max(saving_usd, 0),
        saving_inr=max(saving_inr, 0),
        saving_per_tonne_usd=max(saving_per_t, 0),
        saving_per_tonne_inr=max(saving_per_t * INR_USD, 0),
        saving_pct=max(saving_pct, 0),
        rationale=rationale,
        caveats=caveats,
    )


def analyze_from_csv(rows: list[dict]) -> list[dict]:
    """
    Analyze multiple lot pairs from CSV upload.
    Expects rows with columns: psu_name, cargo_tonnes, destination_port,
    commodity, delivery_window_days.
    Pairs consecutive rows (row 0+1, row 2+3, …).
    """
    results = []
    for i in range(0, len(rows) - 1, 2):
        try:
            lot_a = DemandLot(
                psu_name=rows[i].get("psu_name", f"PSU-{i+1}"),
                cargo_tonnes=int(rows[i].get("cargo_tonnes", 60_000)),
                destination_port=rows[i].get("destination_port", "Paradip"),
                commodity=rows[i].get("commodity", "Coal"),
                delivery_window_days=int(rows[i].get("delivery_window_days", 60)),
            )
            lot_b = DemandLot(
                psu_name=rows[i + 1].get("psu_name", f"PSU-{i+2}"),
                cargo_tonnes=int(rows[i + 1].get("cargo_tonnes", 60_000)),
                destination_port=rows[i + 1].get("destination_port", "Paradip"),
                commodity=rows[i + 1].get("commodity", "Coal"),
                delivery_window_days=int(rows[i + 1].get("delivery_window_days", 60)),
            )
            result = analyze(lot_a, lot_b)
            results.append({
                "pair": f"{lot_a.psu_name} + {lot_b.psu_name}",
                "recommendation": result.recommendation,
                "saving_usd": result.saving_usd,
                "saving_inr": result.saving_inr,
                "saving_pct": result.saving_pct,
                "rationale": result.rationale,
            })
        except Exception as e:
            logger.error(f"CSV pair {i}: {e}")
            results.append({"pair": f"Row {i+1}+{i+2}", "error": str(e)})
    return results
