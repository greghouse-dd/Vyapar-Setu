"""
Vyapar Setu — Forecast Router (fixed to match module-level forecaster API)
=============================================================================
Endpoints:
  POST /forecast           → P10/P50/P90 forecast for a route
  POST /retrain            → re-fit XGBoost on a date window
  GET  /backtest           → full 104-week backtest results
  POST /time-machine       → simulate forecast from a historical date
"""
from __future__ import annotations

import traceback
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

router = APIRouter(prefix="/forecast", tags=["Forecast"])

# ── Request / Response models ─────────────────────────────────────────────────
class ForecastRequest(BaseModel):
    route: str = Field(default="Australia→Paradip (Panamax)", description="Route identifier")
    horizon_weeks: int = Field(default=12, ge=1, le=52)
    bunker_price_override: Optional[float] = Field(default=None, description="Override VLSFO price $/t")
    bdi_override: Optional[float] = Field(default=None, description="Override current BDI value")
    include_shap: bool = Field(default=True)


class RetrainRequest(BaseModel):
    train_start: date = Field(default=date(2020, 1, 6))
    train_end: date = Field(default=date(2023, 12, 25))


class TimeMachineRequest(BaseModel):
    as_of_date: date = Field(description="Simulate forecast from this historical date")
    horizon_weeks: int = Field(default=12, ge=1, le=52)


# ── Lazy-import helpers ───────────────────────────────────────────────────────
def _forecaster_module():
    """Import the forecaster service module (deferred to avoid startup cost)."""
    try:
        import services.forecaster as fc
        return fc
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Forecaster module unavailable: {e}")


def _ensure_model_trained():
    """Ensure a trained model exists, training if necessary."""
    fc = _forecaster_module()
    from pathlib import Path
    import os
    models_dir = Path(os.getenv("MODELS_DIR", "./models"))
    xgb_path = models_dir / "xgb_model.pkl"
    if not xgb_path.exists():
        logger.info("No trained model found — training now (first request may be slow)…")
        try:
            fc.train(save=True)
        except Exception as e:
            logger.warning(f"Training failed: {e} — endpoints will return partial results")


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("", summary="Generate freight rate forecast with P10/P50/P90 bands")
def generate_forecast(req: ForecastRequest) -> dict:
    try:
        _ensure_model_trained()
        fc = _forecaster_module()
        result = fc.forecast(horizon_weeks=req.horizon_weeks)
        result["route"] = req.route
        # Rename forecast_points → forecast for frontend compatibility
        result["forecast"] = result.pop("forecast_points", [])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain", summary="Re-fit XGBoost residual model on a date window")
def retrain_model(req: RetrainRequest) -> dict:
    try:
        fc = _forecaster_module()
        metrics = fc.train(
            train_from=req.train_start.isoformat(),
            train_to=req.train_end.isoformat(),
            save=True,
        )
        return {
            "status": "retrained",
            "train_start": req.train_start.isoformat(),
            "train_end": req.train_end.isoformat(),
            "metrics": {
                "mape_pct": metrics.get("mape_ensemble"),
                "mape_prophet_pct": metrics.get("mape_prophet"),
                "mape_naive_pct": metrics.get("mape_naive"),
                "rmse": metrics.get("rmse_ensemble"),
                "trained_at": metrics.get("trained_at"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtest", summary="Return full hold-out backtest results")
def get_backtest() -> dict:
    try:
        _ensure_model_trained()
        fc = _forecaster_module()
        return fc.run_backtest()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/time-machine", summary="Simulate forecast from a historical date")
def time_machine(req: TimeMachineRequest) -> dict:
    try:
        _ensure_model_trained()
        fc = _forecaster_module()
        result = fc.forecast(
            horizon_weeks=req.horizon_weeks,
            as_of_date=req.as_of_date.isoformat(),
        )
        result["forecast"] = result.pop("forecast_points", [])
        result["time_machine_date"] = req.as_of_date.isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
