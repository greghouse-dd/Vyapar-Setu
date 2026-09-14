"""
Vyapar Setu — Idle Fleet Advisor Router
=========================================
Endpoints:
  POST /idle-advisor   → Returns ranked reposition/backhaul/relet/idle strategies
"""
from __future__ import annotations

import traceback
from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from services.idle_engine import IdleAdvisorRequest, advise

router = APIRouter(prefix="/idle-advisor", tags=["Idle Advisor"])


class IdleAdvisorPayload(BaseModel):
    vessel_class: str = Field(
        default="Panamax",
        description="Handysize | Supramax | Panamax | Capesize",
    )
    current_port: str = Field(default="Haldia")
    dwt: int = Field(default=75_000, ge=20_000, le=200_000)
    last_discharge_date_days_ago: int = Field(default=0, ge=0)
    idle_cost_per_day_usd: float = Field(default=2_500.0)
    vlsfo_price_usd: float = Field(default=620.0)
    forecast_horizon_weeks: int = Field(default=4, ge=1, le=12)
    current_tce_estimate_usd_day: Optional[float] = Field(default=None)
    port_rate_forecasts: Optional[dict[str, float]] = Field(
        default=None,
        description="Override freight rate ($/t) per port for next N weeks",
    )


@router.post("", summary="Recommend optimal strategy for an idle / post-discharge vessel")
def idle_advisor(req: IdleAdvisorPayload) -> dict:
    try:
        advisor_req = IdleAdvisorRequest(
            vessel_class=req.vessel_class,
            current_port=req.current_port,
            dwt=req.dwt,
            last_discharge_date_days_ago=req.last_discharge_date_days_ago,
            idle_cost_per_day_usd=req.idle_cost_per_day_usd,
            vlsfo_price_usd=req.vlsfo_price_usd,
            forecast_horizon_weeks=req.forecast_horizon_weeks,
            current_tce_estimate_usd_day=req.current_tce_estimate_usd_day,
            port_rate_forecasts=req.port_rate_forecasts,
        )
        result = advise(advisor_req)
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
