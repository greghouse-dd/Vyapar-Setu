"""
Vyapar Setu — Pooling Router
==============================
Endpoints:
  POST /pooling/analyze       → JSON body with two demand lots
  POST /pooling/upload-csv    → Multipart CSV upload (multiple lot pairs)
"""
from __future__ import annotations

import csv
import io
import traceback
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel, Field

from services.pooling_engine import DemandLot, analyze, analyze_from_csv

router = APIRouter(prefix="/pooling", tags=["Pooling"])


# ── Request models ─────────────────────────────────────────────────────────────
class DemandLotModel(BaseModel):
    psu_name: str = Field(default="SAIL")
    cargo_tonnes: int = Field(default=55_000, ge=5_000, le=200_000)
    destination_port: str = Field(default="Paradip")
    commodity: str = Field(default="Coal")
    delivery_window_days: int = Field(default=60, ge=7, le=180)
    max_draft_m: Optional[float] = Field(default=None)


class PoolingAnalysisRequest(BaseModel):
    lot_a: DemandLotModel
    lot_b: DemandLotModel


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/analyze", summary="Analyze pooling vs. separate chartering for two PSU lots")
def analyze_pooling(req: PoolingAnalysisRequest) -> dict:
    try:
        lot_a = DemandLot(
            psu_name=req.lot_a.psu_name,
            cargo_tonnes=req.lot_a.cargo_tonnes,
            destination_port=req.lot_a.destination_port,
            commodity=req.lot_a.commodity,
            delivery_window_days=req.lot_a.delivery_window_days,
            max_draft_m=req.lot_a.max_draft_m,
        )
        lot_b = DemandLot(
            psu_name=req.lot_b.psu_name,
            cargo_tonnes=req.lot_b.cargo_tonnes,
            destination_port=req.lot_b.destination_port,
            commodity=req.lot_b.commodity,
            delivery_window_days=req.lot_b.delivery_window_days,
            max_draft_m=req.lot_b.max_draft_m,
        )
        result = analyze(lot_a, lot_b)
        return {
            "recommendation": result.recommendation,
            "feasible": result.feasible,
            "infeasibility_notes": result.infeasibility_notes,
            "separate": {
                "lot_a": {
                    "psu": lot_a.psu_name,
                    "vessel_class": result.lot_a_separate_vessel,
                    "cost_usd": result.lot_a_separate_cost_usd,
                },
                "lot_b": {
                    "psu": lot_b.psu_name,
                    "vessel_class": result.lot_b_separate_vessel,
                    "cost_usd": result.lot_b_separate_cost_usd,
                },
                "total_cost_usd": result.total_separate_cost_usd,
                "total_cost_inr": result.total_separate_cost_usd * 83.5,
            },
            "pooled": {
                "vessel_class": result.pooled_vessel_class,
                "total_cost_usd": result.pooled_cost_usd,
                "lot_a_share_usd": result.lot_a_pooled_share_usd,
                "lot_b_share_usd": result.lot_b_pooled_share_usd,
                "total_cost_inr": result.pooled_cost_usd * 83.5,
            },
            "savings": {
                "saving_usd": result.saving_usd,
                "saving_inr": result.saving_inr,
                "saving_per_tonne_usd": result.saving_per_tonne_usd,
                "saving_per_tonne_inr": result.saving_per_tonne_inr,
                "saving_pct": result.saving_pct,
            },
            "rationale": result.rationale,
            "caveats": result.caveats,
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-csv", summary="Batch pooling analysis from CSV upload")
async def upload_csv(file: UploadFile = File(...)) -> dict:
    try:
        contents = await file.read()
        text = contents.decode("utf-8-sig")   # handle BOM
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if len(rows) < 2:
            raise HTTPException(
                status_code=422,
                detail="CSV must have at least 2 rows (one lot pair).",
            )
        results = analyze_from_csv(rows)
        return {
            "filename": file.filename,
            "rows_processed": len(rows),
            "pairs_analyzed": len(results),
            "results": results,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
