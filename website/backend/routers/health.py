"""
Vyapar Setu — Health & Status Router
"""
from __future__ import annotations

import platform
import sys
from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Health check")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "Vyapar Setu Backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python": sys.version,
        "platform": platform.system(),
    }
