"""
Vyapar Setu — Tender Generation Router
========================================
Endpoints:
  POST /generate-tender              → Returns English .docx
  POST /generate-tender/vernacular   → Returns .zip (English + regional language)
  GET  /audit-log                    → Returns decision log
"""
from __future__ import annotations

import traceback
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from loguru import logger
from pydantic import BaseModel, Field

from services.tender_generator import generate_tender_docx, generate_vernacular_zip

router = APIRouter(prefix="/generate-tender", tags=["Tender"])

# In-memory audit log (in production: persisted to DB)
_audit_log: list[dict] = []


class TenderRequest(BaseModel):
    recommendation: dict = Field(description="Output from /optimizer")
    shap_drivers: list[dict] = Field(default_factory=list)
    request_payload: dict = Field(default_factory=dict)
    ref_number: Optional[str] = None
    generated_by: str = Field(default="Vyapar Setu AI System")


class TenderVernacularRequest(TenderRequest):
    language_override: Optional[str] = Field(
        default=None,
        description="Force language: Odia | Telugu | Bengali | Hindi",
    )
    translated_text: Optional[str] = Field(default=None)


@router.post("", summary="Generate English chartering tender specification (.docx)")
def generate_tender(req: TenderRequest) -> Response:
    try:
        doc_bytes = generate_tender_docx(
            recommendation=req.recommendation,
            shap_drivers=req.shap_drivers,
            request_payload=req.request_payload,
            ref_number=req.ref_number,
            generated_by=req.generated_by,
        )

        # Log to audit trail
        ref = req.ref_number or f"VS/TENDER/{datetime.now().strftime('%Y%m%d')}/AUTO"
        _audit_log.append({
            "ref": ref,
            "action": "generated",
            "generated_by": req.generated_by,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recommendation_summary": {
                "vessel_class": req.recommendation.get("vessel_class"),
                "origin": req.recommendation.get("origin"),
                "total_cost_usd": req.recommendation.get("total_cost_usd"),
            },
            "decision": "pending",
        })

        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="tender_{ref.replace("/", "_")}.docx"',
            },
        )
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vernacular", summary="Generate .zip with English + regional language tender")
def generate_vernacular_tender(req: TenderVernacularRequest) -> Response:
    try:
        english_bytes = generate_tender_docx(
            recommendation=req.recommendation,
            shap_drivers=req.shap_drivers,
            request_payload=req.request_payload,
            ref_number=req.ref_number,
            generated_by=req.generated_by,
        )

        dest_port = req.request_payload.get("destination_port", "Paradip")
        zip_bytes = generate_vernacular_zip(
            english_bytes=english_bytes,
            destination_port=dest_port,
            translated_text=req.translated_text,
            language_override=req.language_override,
        )

        ref = req.ref_number or f"VS/TENDER/{datetime.now().strftime('%Y%m%d')}/VERN"
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="tender_vernacular_{ref.replace("/", "_")}.zip"',
            },
        )
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-log", summary="Get tender generation and decision audit log")
def get_audit_log(limit: int = 50) -> dict:
    return {
        "total_entries": len(_audit_log),
        "entries": _audit_log[-limit:][::-1],   # most recent first
    }


@router.post("/audit-log/decision", summary="Record approve / modify / reject decision")
def record_decision(
    ref: str,
    decision: str,   # approve | modify | reject
    decided_by: str = "Unknown",
    notes: Optional[str] = None,
) -> dict:
    if decision not in ("approve", "modify", "reject"):
        raise HTTPException(status_code=422, detail="decision must be approve | modify | reject")

    for entry in _audit_log:
        if entry["ref"] == ref:
            entry["decision"] = decision
            entry["decided_by"] = decided_by
            entry["decision_timestamp"] = datetime.utcnow().isoformat() + "Z"
            entry["decision_notes"] = notes
            return {"status": "updated", "ref": ref, "decision": decision}

    raise HTTPException(status_code=404, detail=f"Ref '{ref}' not found in audit log")
