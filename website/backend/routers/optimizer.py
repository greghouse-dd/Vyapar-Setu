"""
Vyapar Setu — Optimizer Router
================================
Endpoints:
  POST /optimize                     → Full chartering optimization
  POST /chartering-recommendation    → Lightweight fix/wait/hedge rule
  POST /sensitivity                  → Sensitivity analysis on recommendation
"""
from __future__ import annotations

import traceback
from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from services.milp_optimizer import (
    OptimizationRequest,
    get_chartering_quick_recommendation,
    optimize,
)

router = APIRouter(prefix="/optimizer", tags=["Optimizer"])


# ── Request models ────────────────────────────────────────────────────────────
class OptimizeRequest(BaseModel):
    destination_port: str = Field(default="Paradip", description="Indian destination port")
    cargo_tonnes: int = Field(default=65_000, ge=10_000, le=300_000)
    commodity: str = Field(default="Coal")
    latest_arrival_date_days: int = Field(default=60, ge=7, le=180)
    budget_cap_usd: Optional[float] = Field(default=None)
    safety_stock_floor_pct: float = Field(default=0.10)
    vlsfo_price_usd_per_t: float = Field(default=620.0)
    current_spot_rate_usd_per_t: float = Field(default=18.5)
    allow_ffa_hedge: bool = Field(default=True)
    exclude_origins: list[str] = Field(default_factory=list)
    force_vessel_class: Optional[str] = Field(default=None)


class QuickRecommendationRequest(BaseModel):
    forecast_trend: str = Field(
        default="rising",
        description="rising | falling | stable",
    )
    weeks_to_delivery: int = Field(default=8, ge=1, le=52)
    current_rate_usd: float = Field(default=18.5)
    ffa_available: bool = Field(default=True)


class SensitivityRequest(BaseModel):
    base_recommendation: dict = Field(description="Output from /optimize recommendation")
    rate_change_pct: float = Field(default=10.0, description="±% change in freight rate")
    bunker_change_pct: float = Field(default=15.0)


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("", summary="Full chartering optimization — MILP cost enumeration")
def run_optimizer(req: OptimizeRequest) -> dict:
    try:
        opt_req = OptimizationRequest(
            destination_port=req.destination_port,
            cargo_tonnes=req.cargo_tonnes,
            latest_arrival_date_days=req.latest_arrival_date_days,
            budget_cap_usd=req.budget_cap_usd,
            safety_stock_floor_pct=req.safety_stock_floor_pct,
            vlsfo_price_usd_per_t=req.vlsfo_price_usd_per_t,
            current_spot_rate_usd_per_t=req.current_spot_rate_usd_per_t,
            allow_ffa_hedge=req.allow_ffa_hedge,
            exclude_origins=req.exclude_origins,
            force_vessel_class=req.force_vessel_class,
        )
        result = optimize(opt_req)
        result["commodity"] = req.commodity
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chartering-recommendation", summary="Lightweight fix/wait/hedge rule")
def chartering_recommendation(req: QuickRecommendationRequest) -> dict:
    try:
        trend = req.forecast_trend.lower()
        if trend not in ("rising", "falling", "stable"):
            raise HTTPException(
                status_code=422,
                detail="forecast_trend must be 'rising', 'falling', or 'stable'",
            )
        return get_chartering_quick_recommendation(
            forecast_trend=trend,
            weeks_to_delivery=req.weeks_to_delivery,
            current_rate_usd=req.current_rate_usd,
            ffa_available=req.ffa_available,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sensitivity", summary="Sensitivity analysis — rate and bunker impact")
def sensitivity_analysis(req: SensitivityRequest) -> dict:
    try:
        base_cost = req.base_recommendation.get("total_cost_usd", 0)
        cargo_t = req.base_recommendation.get("lot_size_tonnes", 1)

        rate_impact = base_cost * (req.rate_change_pct / 100) * 0.75
        bunker_impact = base_cost * (req.bunker_change_pct / 100) * 0.18

        return {
            "base_cost_usd": base_cost,
            "rate_change_pct": req.rate_change_pct,
            "bunker_change_pct": req.bunker_change_pct,
            "rate_upside_scenario": {
                "total_cost_usd": round(base_cost + rate_impact, 0),
                "delta_per_tonne_usd": round(rate_impact / max(cargo_t, 1), 2),
                "recommendation": "Hedge with FFA to cap exposure",
            },
            "rate_downside_scenario": {
                "total_cost_usd": round(base_cost - rate_impact, 0),
                "delta_per_tonne_usd": round(-rate_impact / max(cargo_t, 1), 2),
                "recommendation": "Consider waiting 2–4 weeks before fixing",
            },
            "bunker_upside_scenario": {
                "total_cost_usd": round(base_cost + bunker_impact, 0),
                "delta_per_tonne_usd": round(bunker_impact / max(cargo_t, 1), 2),
                "recommendation": "Consider shorter voyage (Indonesia origin) to reduce bunker exposure",
            },
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
