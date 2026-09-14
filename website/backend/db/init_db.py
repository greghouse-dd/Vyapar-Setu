"""
Vyapar Setu — Database Schema + Seed Data
Defines all ORM models and seeds the port-constraint lookup table.
Run once with: python -m db.init_db
"""
from __future__ import annotations

import json
from datetime import datetime

from loguru import logger
from sqlalchemy import (
    JSON, Boolean, Column, DateTime, Float, Integer, String, Text, func
)

from db.database import Base, SessionLocal, engine


# ═══════════════════════════════════════════════════════════════════════════════
#  ORM MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class WeeklyFeature(Base):
    """
    Time-indexed feature store row.
    One row per (route × vessel_class × week).
    """
    __tablename__ = "weekly_features"

    id                    = Column(Integer, primary_key=True, index=True)
    route_key             = Column(String(64), index=True, nullable=False)
    vessel_class          = Column(String(16), nullable=False)
    week_date             = Column(String(16), index=True, nullable=False)  # ISO date

    # Baltic indices
    bpi_5tc               = Column(Float, nullable=True)    # Baltic Panamax Index ($/day)
    bci_5tc               = Column(Float, nullable=True)    # Baltic Capesize Index ($/day)
    bdi                   = Column(Float, nullable=True)    # Baltic Dry Index (composite)

    # Freight
    freight_rate_usd_t    = Column(Float, nullable=True)    # All-in $/tonne for this route

    # Fuel
    vlsfo_sgp_usd_t       = Column(Float, nullable=True)    # VLSFO Singapore $/tonne

    # Port / congestion
    port_congestion_days  = Column(Float, nullable=True)    # Paradip berth wait days

    # Macro
    usd_inr               = Column(Float, nullable=True)

    # Weather / risk
    cyclone_dummy         = Column(Integer, nullable=True)  # 1 if cyclone season active
    red_sea_disruption    = Column(Integer, nullable=True)  # 1 for Jan–Mar 2024

    # Metadata
    data_source           = Column(String(32), default="synthetic_public_proxy")
    created_at            = Column(DateTime, default=datetime.utcnow)


class PortConstraint(Base):
    """
    Versioned port draft / DWT / handling-rate constraint table.
    Keyed by (port_name × version_date).
    """
    __tablename__ = "port_constraints"

    id                      = Column(Integer, primary_key=True)
    port_name               = Column(String(32), index=True, nullable=False)
    version_date            = Column(String(16), nullable=False)   # ISO date
    max_draft_m             = Column(Float, nullable=False)
    max_dwt_tonnes          = Column(Integer, nullable=False)
    max_vessel_class        = Column(String(16), nullable=False)
    cargo_handling_rate_tpd = Column(Integer, nullable=False)
    laytime_allowed_days    = Column(Float, nullable=False)
    demurrage_rate_usd_day  = Column(Integer, nullable=False)
    notes                   = Column(Text, nullable=True)
    is_current              = Column(Boolean, default=True)


class DecisionLog(Base):
    """
    Immutable audit trail for every approve / modify / reject action.
    Supports CVC-compliant decision accountability.
    """
    __tablename__ = "decision_log"

    id           = Column(Integer, primary_key=True, index=True)
    timestamp    = Column(DateTime, default=datetime.utcnow, index=True)
    tender_ref   = Column(String(64), nullable=False, index=True)
    route        = Column(String(64), nullable=True)
    recommendation = Column(Text, nullable=True)        # JSON blob
    action       = Column(String(16), nullable=False)   # approved/modified/rejected
    officer_name = Column(String(64), nullable=False)
    notes        = Column(Text, nullable=True)


class VoiceNoteLog(Base):
    """Logs every voice-note ingestion with transcript + confidence score."""
    __tablename__ = "voice_note_log"

    id                  = Column(Integer, primary_key=True)
    timestamp           = Column(DateTime, default=datetime.utcnow)
    port_name           = Column(String(32), index=True)
    reporter_role       = Column(String(32))
    transcript_original = Column(Text)
    transcript_english  = Column(Text)
    confidence_score    = Column(Float)
    structured_event    = Column(JSON, nullable=True)
    flagged_for_review  = Column(Boolean, default=False)


# ═══════════════════════════════════════════════════════════════════════════════
#  PORT CONSTRAINT SEED DATA (sourced from publicly available port-authority data)
# ═══════════════════════════════════════════════════════════════════════════════

PORT_CONSTRAINT_SEED = [
    # Paradip — post-Sept 2026 Capesize milestone (Section 1.2 of CargoSense v5)
    {
        "port_name": "Paradip", "version_date": "2026-09-06",
        "max_draft_m": 16.5, "max_dwt_tonnes": 180_000,
        "max_vessel_class": "Capesize",          # partially-laden Capesize now feasible
        "cargo_handling_rate_tpd": 35_000,
        "laytime_allowed_days": 4.0,
        "demurrage_rate_usd_day": 20_000,
        "notes": (
            "Western Dock-1; 16.5 m draft (tiered); full Capesize pending 18.5 m dredge. "
            "First Capesize: MV Mineral Kwangyang, 180,513 DWT, 152,702 MT from Hay Point AUS, berthed 2026-09-06."
        ),
        "is_current": True,
    },
    # Dhamra — deep-draft Capesize-capable
    {
        "port_name": "Dhamra", "version_date": "2024-01-01",
        "max_draft_m": 18.4, "max_dwt_tonnes": 200_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 40_000,
        "laytime_allowed_days": 5.0,
        "demurrage_rate_usd_day": 22_000,
        "notes": "Demonstrated: 186,782 MT coking coal parcel for Tata Steel (18.4 m draft).",
        "is_current": True,
    },
    # Vizag
    {
        "port_name": "Vizag", "version_date": "2024-01-01",
        "max_draft_m": 17.0, "max_dwt_tonnes": 180_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 30_000,
        "laytime_allowed_days": 4.5,
        "demurrage_rate_usd_day": 18_000,
        "notes": "Established deep-water port; mixed Panamax/Capesize traffic. Placeholder fidelity.",
        "is_current": True,
    },
    # Gangavaram
    {
        "port_name": "Gangavaram", "version_date": "2024-01-01",
        "max_draft_m": 17.0, "max_dwt_tonnes": 180_000,
        "max_vessel_class": "Capesize",
        "cargo_handling_rate_tpd": 28_000,
        "laytime_allowed_days": 4.0,
        "demurrage_rate_usd_day": 18_000,
        "notes": "Deep-water; 7 MT/yr coking coal FY24. Placeholder fidelity.",
        "is_current": True,
    },
    # Gopalpur — shallower, Supramax ceiling
    {
        "port_name": "Gopalpur", "version_date": "2024-01-01",
        "max_draft_m": 12.0, "max_dwt_tonnes": 60_000,
        "max_vessel_class": "Supramax",
        "cargo_handling_rate_tpd": 15_000,
        "laytime_allowed_days": 3.5,
        "demurrage_rate_usd_day": 12_000,
        "notes": "Historically Handysize/Supramax. Placeholder fidelity.",
        "is_current": True,
    },
    # Sagar-Sandheads — lightering node, not a berth
    {
        "port_name": "Sagar-Sandheads", "version_date": "2024-01-01",
        "max_draft_m": 9.0, "max_dwt_tonnes": 30_000,
        "max_vessel_class": "Handysize",
        "cargo_handling_rate_tpd": 8_000,
        "laytime_allowed_days": 2.0,
        "demurrage_rate_usd_day": 8_000,
        "notes": "Lightering/transshipment node for Haldia approaches. Modeled as a transshipment node.",
        "is_current": True,
    },
    # Haldia — river port, shallow
    {
        "port_name": "Haldia", "version_date": "2024-01-01",
        "max_draft_m": 8.5, "max_dwt_tonnes": 25_000,
        "max_vessel_class": "Handysize",
        "cargo_handling_rate_tpd": 10_000,
        "laytime_allowed_days": 3.0,
        "demurrage_rate_usd_day": 10_000,
        "notes": "River port; shallow draft. Larger parcels via Sagar-Sandheads lightering. Placeholder fidelity.",
        "is_current": True,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
#  INITIALISER
# ═══════════════════════════════════════════════════════════════════════════════

def init_db() -> None:
    """Create all tables and seed the port-constraint lookup table."""
    logger.info("Creating database schema …")
    Base.metadata.create_all(bind=engine)
    logger.success("Schema created (or already exists).")

    db = SessionLocal()
    try:
        existing = db.query(PortConstraint).count()
        if existing == 0:
            logger.info("Seeding port constraint lookup table …")
            for row in PORT_CONSTRAINT_SEED:
                db.add(PortConstraint(**row))
            db.commit()
            logger.success(f"Seeded {len(PORT_CONSTRAINT_SEED)} port constraint rows.")
        else:
            logger.info(f"Port constraint table already has {existing} rows — skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("✅ Database initialised successfully.")
