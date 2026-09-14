"""
Vyapar Setu — FastAPI Application Entry Point
==============================================
Run with:
  cd website/backend
  uvicorn main:app --reload --host 0.0.0.0 --port 8001

API Documentation:
  http://localhost:8001/docs     (Swagger UI)
  http://localhost:8001/redoc   (ReDoc)
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# ── Load environment variables ────────────────────────────────────────────────
_env_file = Path(__file__).parent / ".env"
load_dotenv(_env_file if _env_file.exists() else Path(__file__).parent / ".env.example")

# ── Import routers ────────────────────────────────────────────────────────────
from routers.forecast import router as forecast_router
from routers.health import router as health_router
from routers.idle_advisor import router as idle_router
from routers.optimizer import router as optimizer_router
from routers.pooling import router as pooling_router
from routers.tender import router as tender_router
from routers.vernacular import router as vernacular_router


# ── Startup / Shutdown ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Vyapar Setu API starting up…")

    # Initialize database
    try:
        from db.init_db import init_db
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  DB init skipped: {e}")

    # Pre-generate synthetic data if not already present
    try:
        data_dir = Path(__file__).parent / "data" / "raw"
        if not (data_dir / "aus_paradip_panamax_weekly.csv").exists():
            logger.info("📊 Generating synthetic dataset…")
            from services.data_pipeline import generate_weekly_features
            generate_weekly_features(save=True)
            logger.info("✅ Dataset generated")
        else:
            logger.info("✅ Synthetic dataset already exists")
    except Exception as e:
        logger.warning(f"⚠️  Data pipeline skipped: {e}")

    yield   # Application runs

    logger.info("👋 Vyapar Setu API shutting down…")


# ── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI(
    title="Vyapar Setu API",
    description=(
        "**Vyapar Setu** — Intelligent Freight Forecasting & Vessel Chartering Optimization Platform.\n\n"
        "Built for SIH 2026 | Powered by Prophet + XGBoost + OR-Tools + Sarvam AI.\n\n"
        "All endpoints support CORS for the frontend served on `http://localhost:8000`."
    ),
    version="1.0.0",
    contact={
        "name": "Vyapar Setu Team — SIH 2026",
        "url": "https://github.com/greghouse-dd/Vyapar-Setu",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allow frontend on port 8000 and any localhost origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "*",   # dev convenience — restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(forecast_router)
app.include_router(optimizer_router)
app.include_router(pooling_router)
app.include_router(idle_router)
app.include_router(tender_router)
app.include_router(vernacular_router)


# ── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "service": "Vyapar Setu API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "forecast":    "/forecast",
            "optimizer":   "/optimizer",
            "pooling":     "/pooling/analyze",
            "idle_advisor":"/idle-advisor",
            "tender":      "/generate-tender",
            "vernacular":  "/vernacular/voice-query",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
