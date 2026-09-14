"""
Vyapar Setu Backend — Pydantic Request/Response Schemas
All API models are defined here for consistency and auto-generated OpenAPI docs.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
#  ENUMS
# ═══════════════════════════════════════════════════════════

class VesselClass(str, Enum):
    handysize = "Handysize"
    supramax  = "Supramax"
    panamax   = "Panamax"
    capesize  = "Capesize"


class CharterTiming(str, Enum):
    fix_now   = "fix_now"
    wait_2w   = "wait_2w"
    wait_4w   = "wait_4w"
    ffa_hedge = "ffa_hedge"


class PortName(str, Enum):
    paradip        = "Paradip"
    dhamra         = "Dhamra"
    vizag          = "Vizag"
    gangavaram     = "Gangavaram"
    gopalpur       = "Gopalpur"
    sagar_sandheads= "Sagar-Sandheads"
    haldia         = "Haldia"


class OriginCountry(str, Enum):
    australia  = "Australia"
    indonesia  = "Indonesia"
    usa        = "USA"
    mozambique = "Mozambique"
    russia     = "Russia"       # flagged – sanctions-compliance required


class Language(str, Enum):
    hindi   = "hi-IN"
    odia    = "or-IN"
    telugu  = "te-IN"
    bengali = "bn-IN"


class IdleStrategy(str, Enum):
    ballast_reposition = "ballast_reposition"
    backhaul           = "backhaul"
    relet              = "relet"
    idle_at_anchor     = "idle_at_anchor"


# ═══════════════════════════════════════════════════════════
#  SHARED SUB-MODELS
# ═══════════════════════════════════════════════════════════

class SHAPDriver(BaseModel):
    feature: str
    contribution_usd_per_tonne: float
    direction: str   # "positive" | "negative"
    description: str


class ProbabilisticBand(BaseModel):
    p10: float = Field(..., description="10th percentile forecast ($/tonne)")
    p50: float = Field(..., description="50th percentile forecast ($/tonne)")
    p90: float = Field(..., description="90th percentile forecast ($/tonne)")


# ═══════════════════════════════════════════════════════════
#  FORECAST
# ═══════════════════════════════════════════════════════════

class ForecastRequest(BaseModel):
    origin:        OriginCountry = OriginCountry.australia
    destination:   PortName      = PortName.paradip
    vessel_class:  VesselClass   = VesselClass.panamax
    horizon_weeks: int           = Field(12, ge=1, le=26)
    as_of_date:    Optional[date] = None   # None = today (live mode)


class ForecastPoint(BaseModel):
    week:  str              # ISO date string "2024-03-04"
    p10:   float
    p50:   float
    p90:   float
    actual: Optional[float] = None   # filled in Time-Machine mode


class ForecastResponse(BaseModel):
    route:           str
    horizon_weeks:   int
    as_of_date:      str
    current_rate:    float
    forecast_points: List[ForecastPoint]
    shap_drivers:    List[SHAPDriver]
    trend_direction: str    # "rising" | "falling" | "stable"
    cyclone_warning: bool
    model_info:      Dict[str, Any]


class RetrainRequest(BaseModel):
    train_from: Optional[date] = None
    train_to:   Optional[date] = None
    route:      str = "AUS_PARADIP_PANAMAX"


class RetrainResponse(BaseModel):
    status:            str
    mape_ensemble:     float
    mape_prophet_only: float
    mape_naive:        float
    rmse_ensemble:     float
    train_weeks:       int
    test_weeks:        int
    message:           str


class BacktestResponse(BaseModel):
    window_start:           str
    window_end:             str
    total_weeks:            int
    simulated_lots:         int
    mape_ensemble:          float
    mape_prophet_only:      float
    mape_naive_lastvalue:   float
    saving_usd_per_tonne_vs_charter_immediately: float
    saving_inr_per_tonne_vs_charter_immediately: float
    saving_pct_vs_charter_immediately:           float
    saving_usd_per_tonne_vs_naive:               float
    red_sea_signal_lead_days:                    int
    stress_test_supercycle_note:                 str
    methodology_note:                            str


# ═══════════════════════════════════════════════════════════
#  OPTIMIZER (CP-SAT constraint optimization)
# ═══════════════════════════════════════════════════════════

class OptimizeRequest(BaseModel):
    destination:      PortName      = PortName.paradip
    cargo_tonnes:     int           = Field(65_000, ge=10_000, le=200_000)
    required_by_date: Optional[date] = None
    budget_usd:       Optional[float] = None
    safety_stock_days: int          = Field(30, ge=0, le=90)
    preferred_origin: Optional[OriginCountry] = None
    include_russia:   bool          = False


class PortConstraint(BaseModel):
    port:                 PortName
    max_draft_m:          float
    max_dwt_tonnes:       int
    max_vessel_class:     VesselClass
    cargo_handling_rate_tpd: int    # tonnes per day
    laytime_allowed_days: float
    demurrage_rate_usd_per_day: int


class OptimizeResponse(BaseModel):
    recommendation:    str
    vessel_class:      VesselClass
    charter_timing:    CharterTiming
    lot_size_tonnes:   int
    origin:            OriginCountry
    freight_cost_usd:  float
    freight_cost_inr:  float
    demurrage_cost_usd: float
    quality_penalty_usd: float
    total_cost_usd:    float
    total_cost_inr:    float
    cost_per_tonne_usd: float
    cost_per_tonne_inr: float
    port_constraint:   PortConstraint
    rationale:         str
    shap_drivers:      List[SHAPDriver]
    alternatives:      List[Dict[str, Any]]
    fix_now_wait_hedge: Dict[str, Any]


# ═══════════════════════════════════════════════════════════
#  POOLING
# ═══════════════════════════════════════════════════════════

class DemandLot(BaseModel):
    psu:             str     = Field(..., description="e.g. SAIL or RINL")
    cargo_tonnes:    int     = Field(..., ge=10_000, le=150_000)
    destination:     PortName
    required_by:     date
    max_rate_usd_t:  Optional[float] = None


class PoolingRequest(BaseModel):
    lots: List[DemandLot] = Field(..., min_length=2, max_length=5)


class PoolingResponse(BaseModel):
    recommendation:       str          # "pool" | "separate"
    separate_cost_usd:    float
    pooled_cost_usd:      float
    saving_usd:           float
    saving_inr:           float
    saving_per_tonne_usd: float
    saving_per_tonne_inr: float
    saving_pct:           float
    pooled_vessel_class:  Optional[VesselClass]
    pooled_destination:   Optional[PortName]
    feasibility_notes:    List[str]
    demand_window_overlap: bool
    rationale:            str
    separate_breakdown:   List[Dict[str, Any]]


# ═══════════════════════════════════════════════════════════
#  IDLE / DEADHEADING ADVISOR
# ═══════════════════════════════════════════════════════════

class IdleAdvisorRequest(BaseModel):
    current_port:      PortName
    vessel_class:      VesselClass   = VesselClass.panamax
    vessel_dwt:        int           = 75_000
    discharge_date:    Optional[date] = None
    horizon_weeks:     int           = Field(4, ge=1, le=8)


class IdleOption(BaseModel):
    rank:              int
    strategy:          IdleStrategy
    target_port:       Optional[PortName]
    description:       str
    ballast_cost_usd:  float
    expected_earning_usd: float
    net_value_usd:     float
    net_value_inr:     float
    confidence_p10:    float
    confidence_p90:    float
    days_to_execute:   int
    rationale:         str


class IdleAdvisorResponse(BaseModel):
    vessel_info:       Dict[str, Any]
    analysis_date:     str
    ranked_options:    List[IdleOption]
    recommended:       IdleOption
    forecast_summary:  Dict[str, Any]


# ═══════════════════════════════════════════════════════════
#  TENDER GENERATION
# ═══════════════════════════════════════════════════════════

class TenderRequest(BaseModel):
    psu_name:          str           = "SAIL"
    destination:       PortName      = PortName.paradip
    cargo_type:        str           = "Coking Coal (HCC)"
    lot_size_tonnes:   int           = 65_000
    vessel_class:      VesselClass   = VesselClass.panamax
    freight_ceiling_usd_per_tonne: float = 25.0
    delivery_window_start: Optional[date] = None
    delivery_window_end:   Optional[date] = None
    quality_specs:     Optional[Dict[str, Any]] = None
    generate_vernacular: bool         = False
    vernacular_language: Language     = Language.odia


class TenderAuditAction(str, Enum):
    approved  = "approved"
    modified  = "modified"
    rejected  = "rejected"


class TenderAuditRequest(BaseModel):
    tender_ref:  str
    action:      TenderAuditAction
    officer_name: str
    notes:       Optional[str] = None


class AuditEntry(BaseModel):
    id:            int
    timestamp:     str
    tender_ref:    str
    action:        str
    officer_name:  str
    notes:         Optional[str]


# ═══════════════════════════════════════════════════════════
#  VERNACULAR / SARVAM
# ═══════════════════════════════════════════════════════════

class VoiceQueryResponse(BaseModel):
    transcript_original:  str
    transcript_english:   str
    confidence_score:     float
    answer_english:       str
    answer_translated:    str
    language_detected:    str
    audio_base64:         Optional[str] = None   # Bulbul TTS output
    shap_context:         Optional[List[SHAPDriver]] = None
    low_confidence_flag:  bool = False
    audit_logged:         bool = True


class TranslateTenderRequest(BaseModel):
    english_text:  str
    target_language: Language
    port_context:  Optional[PortName] = None


class VoiceNoteIngestRequest(BaseModel):
    port:           PortName
    reporter_role:  str        = "field_agent"
    audio_base64:   str        # base64-encoded audio
    language_hint:  Optional[Language] = None


class VoiceNoteIngestResponse(BaseModel):
    transcript:           str
    english_translation:  str
    confidence_score:     float
    structured_event: Dict[str, Any]
    flagged_for_review:   bool
    feature_store_updated: bool


# ═══════════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    status:          str
    version:         str
    environment:     str
    database:        str
    forecast_model:  str
    sarvam_mode:     str    # "live" | "mock"
    data_loaded:     bool
    uptime_seconds:  float
    last_retrain:    Optional[str]
