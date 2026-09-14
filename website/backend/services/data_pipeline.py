"""
Vyapar Setu — Data Pipeline
===========================
Generates a realistic synthetic weekly dataset for 2020-01-06 → 2024-12-30
(261 observations) based on the real distributional profile of Baltic indices,
bunker prices, and Bay of Bengal cyclone seasonality.

IMPORTANT: This is a public-proxy / synthetic dataset, NOT real Baltic Exchange
data (which is a licensed product). The data is generated from realistic
statistical distributions calibrated to the historical range of these indices.
The model will train on this data and report whatever MAPE it actually achieves
— the result is NOT engineered to match a target figure.

Run this module directly to (re-)generate all raw CSVs:
    python -m services.data_pipeline
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

# ── Seed for reproducibility of the *data* (not the metric result)
RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RAW_DIR  = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _mean_reverting_walk(
    n: int,
    start: float,
    long_run_mean: float,
    mean_reversion_speed: float = 0.05,
    volatility: float = 0.04,
) -> np.ndarray:
    """Ornstein-Uhlenbeck discrete approximation (log-space for positivity)."""
    log_vals = np.empty(n)
    log_vals[0] = np.log(start)
    log_mean = np.log(long_run_mean)
    for t in range(1, n):
        log_vals[t] = (
            log_vals[t - 1]
            + mean_reversion_speed * (log_mean - log_vals[t - 1])
            + volatility * rng.standard_normal()
        )
    return np.exp(log_vals)


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE WEEKLY DATASET
# ══════════════════════════════════════════════════════════════════════════════

def generate_weekly_features(save: bool = True) -> pd.DataFrame:
    """
    Generate 261 weekly observations of all model features.
    Returns a cleaned DataFrame ready for training.
    """
    weeks = pd.date_range("2020-01-06", "2024-12-30", freq="W-MON")
    n = len(weeks)
    df = pd.DataFrame({"week_date": weeks})

    # ── Baltic Panamax Index BPI-5TC ($/day) ─────────────────────────────────
    # Historical range: ~$5,000–$35,000; long-run mean ~$12,000
    bpi = _mean_reverting_walk(n, start=12_000, long_run_mean=12_000,
                               mean_reversion_speed=0.04, volatility=0.08)

    # Layer 1: COVID-19 freight collapse (Mar–Jun 2020, weeks 9–26)
    covid_shock = np.ones(n)
    covid_shock[9:26] = np.linspace(0.55, 0.75, 17)

    # Layer 2: 2021 BDI supercycle (May–Nov 2021, weeks 65–95)
    supercycle = np.ones(n)
    peak_idx = 80
    for i in range(55, 100):
        dist = abs(i - peak_idx)
        supercycle[i] = 1.0 + max(0, 2.2 - dist * 0.08)

    # Layer 3: Red Sea / Panama disruption signal (Jan–Mar 2024, weeks 207–220)
    red_sea = np.ones(n)
    for i in range(207, 225):
        dist = abs(i - 213)
        red_sea[i] = 1.0 + max(0, 0.65 - dist * 0.05)

    bpi = bpi * covid_shock * supercycle * red_sea
    bpi = np.clip(bpi, 3_000, 45_000)
    df["bpi_5tc"] = np.round(bpi, 0)

    # ── Baltic Capesize Index BCI-5TC ($/day) ─────────────────────────────────
    # Correlated with BPI but more volatile
    noise = rng.standard_normal(n) * 0.03
    bci = bpi * (1.15 + noise) * (1 + rng.standard_normal(n) * 0.12)
    bci = np.clip(bci, 2_000, 60_000)
    df["bci_5tc"] = np.round(bci, 0)

    # ── Composite BDI (weighted average) ─────────────────────────────────────
    # BDI = 0.4 × Capesize + 0.3 × Panamax + 0.3 × others (simplified)
    df["bdi"] = np.round(0.4 * df["bci_5tc"] + 0.35 * df["bpi_5tc"]
                         + 0.25 * (df["bpi_5tc"] * 0.8), 0)

    # ── VLSFO Singapore ($/tonne) ─────────────────────────────────────────────
    # Historical: ~$300 (COVID low) → ~$850 peak → ~$550 average
    vlsfo = _mean_reverting_walk(n, start=550, long_run_mean=530,
                                 mean_reversion_speed=0.06, volatility=0.05)
    vlsfo[9:26]   *= np.linspace(0.65, 0.80, 17)    # COVID low
    vlsfo[90:110] *= np.linspace(1.0, 1.35, 20)     # 2021-22 energy spike
    vlsfo[130:150] *= np.linspace(1.35, 1.05, 20)   # gradual reduction
    vlsfo = np.clip(vlsfo, 280, 900)
    df["vlsfo_sgp_usd_t"] = np.round(vlsfo, 1)

    # ── USD / INR ─────────────────────────────────────────────────────────────
    usd_inr = _mean_reverting_walk(n, start=71.5, long_run_mean=82.0,
                                   mean_reversion_speed=0.01, volatility=0.006)
    usd_inr = np.clip(usd_inr, 70, 87)
    df["usd_inr"] = np.round(usd_inr, 2)

    # ── Bay of Bengal Cyclone Dummy ───────────────────────────────────────────
    # Cyclone season: May–Nov; higher prob Jun-Oct
    month = df["week_date"].dt.month
    cyclone_prob = np.where((month >= 5) & (month <= 11), 0.28, 0.04)
    df["cyclone_dummy"] = rng.binomial(1, cyclone_prob).astype(int)

    # ── Port Congestion Index (Paradip berth wait days) ───────────────────────
    # Seasonal: higher in Jul–Oct (monsoon), lower Jan–Mar
    base_congestion = 2.0 + 1.2 * np.sin((month.values - 4) * np.pi / 6)
    congestion_noise = rng.exponential(0.5, n)
    df["port_congestion_paradip_days"] = np.round(
        np.clip(base_congestion + congestion_noise, 0.5, 8.0), 1
    )

    # ── Red Sea / Panama Disruption Flag ─────────────────────────────────────
    df["red_sea_disruption"] = 0
    df.loc[(df["week_date"] >= "2023-12-01") & (df["week_date"] <= "2024-03-31"),
           "red_sea_disruption"] = 1

    # ── Freight Rate $/tonne (Australia → Paradip, Panamax, ~65,000 DWT) ─────
    # Voyage economics: BPI-5TC drives time-charter equivalent cost.
    # Voyage distance AUS→Paradip ≈ 4,800 nm @ 13 knots = ~15.4 sea days
    # + 4 days port = ~19.4 voyage days total
    voyage_days = 19.4
    cargo_tonnes = 65_000
    bunker_consumption_tpd = 28  # MT/day (Panamax at sea speed)
    tc_cost_per_tonne = (df["bpi_5tc"] * voyage_days) / cargo_tonnes
    fuel_cost_per_tonne = (df["vlsfo_sgp_usd_t"] * bunker_consumption_tpd
                           * voyage_days) / cargo_tonnes
    port_dues = 0.80  # $/tonne constant
    broker_commission = tc_cost_per_tonne * 0.025  # 2.5% brokerage

    freight_rate = tc_cost_per_tonne + fuel_cost_per_tonne + port_dues + broker_commission
    # Congestion premium (non-linear: high congestion is disproportionately costly)
    freight_rate += (df["port_congestion_paradip_days"] ** 1.3) * 0.08
    # Cyclone premium
    freight_rate += df["cyclone_dummy"] * rng.uniform(0.6, 1.2, n)
    # Red Sea premium
    freight_rate += df["red_sea_disruption"] * rng.uniform(1.2, 2.5, n)
    # Spot market noise: broker negotiation spread (~4-8% of base rate)
    spot_noise = rng.normal(0, 0.06, n) * freight_rate
    freight_rate = freight_rate + spot_noise
    # Supply-demand imbalance regime noise (autocorrelated)
    regime_noise = _mean_reverting_walk(n, start=1.0, long_run_mean=1.0,
                                        mean_reversion_speed=0.1, volatility=0.04)
    freight_rate = freight_rate * regime_noise

    df["freight_rate_usd_t"] = np.round(np.clip(freight_rate, 6.0, 55.0), 2)

    # ── Metadata ─────────────────────────────────────────────────────────────
    df["route_key"]    = "AUS_PARADIP_PANAMAX"
    df["vessel_class"] = "Panamax"
    df["data_source"]  = "synthetic_public_proxy"

    df["week_date"] = df["week_date"].dt.strftime("%Y-%m-%d")

    # ── Lag features ─────────────────────────────────────────────────────────
    for col in ["bpi_5tc", "bci_5tc", "vlsfo_sgp_usd_t", "freight_rate_usd_t"]:
        for lag in [1, 2, 3, 4, 8, 12]:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)

    # ── Rolling statistics (4-week and 12-week windows) ───────────────────────
    for col in ["bpi_5tc", "vlsfo_sgp_usd_t", "freight_rate_usd_t"]:
        df[f"{col}_roll4_mean"]  = df[col].rolling(4,  min_periods=2).mean()
        df[f"{col}_roll4_std"]   = df[col].rolling(4,  min_periods=2).std().fillna(0)
        df[f"{col}_roll12_mean"] = df[col].rolling(12, min_periods=4).mean()
        df[f"{col}_roll12_std"]  = df[col].rolling(12, min_periods=4).std().fillna(0)

    # ── Momentum features ─────────────────────────────────────────────────────
    df["bpi_momentum_4w"]  = df["bpi_5tc"] - df["bpi_5tc"].shift(4)
    df["bpi_momentum_12w"] = df["bpi_5tc"] - df["bpi_5tc"].shift(12)
    df["vlsfo_momentum_4w"] = df["vlsfo_sgp_usd_t"] - df["vlsfo_sgp_usd_t"].shift(4)

    # ── Cross-feature: Bunker × BPI interaction ───────────────────────────────
    df["bunker_bpi_interaction"] = (
        df["vlsfo_sgp_usd_t"].shift(1) * df["bpi_5tc"].shift(1)
    ) / 1e6  # scale to reasonable range

    # ── USD/INR rate of change ────────────────────────────────────────────────
    df["usd_inr_change_4w"] = df["usd_inr"] - df["usd_inr"].shift(4)

    # ── Z-score normalization of BPI (freight market regime indicator) ────────
    bpi_roll_mean = df["bpi_5tc"].rolling(26, min_periods=8).mean()
    bpi_roll_std  = df["bpi_5tc"].rolling(26, min_periods=8).std().replace(0, 1)
    df["bpi_zscore_26w"] = (df["bpi_5tc"] - bpi_roll_mean) / bpi_roll_std

    # ── Calendar features ─────────────────────────────────────────────────────
    df["week_of_year"] = pd.to_datetime(df["week_date"]).dt.isocalendar().week.astype(int)
    df["month"]        = pd.to_datetime(df["week_date"]).dt.month
    # Sine/cosine encoding of week-of-year for cyclical representation
    df["week_sin"] = np.sin(2 * np.pi * df["week_of_year"] / 52)
    df["week_cos"] = np.cos(2 * np.pi * df["week_of_year"] / 52)

    # Drop rows with NaN lags (first 12 weeks)
    df = df.dropna().reset_index(drop=True)

    if save:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        PROC_DIR.mkdir(parents=True, exist_ok=True)

        raw_path  = RAW_DIR  / "aus_paradip_panamax_weekly.csv"
        proc_path = PROC_DIR / "weekly_features.csv"

        df.to_csv(raw_path,  index=False)
        df.to_csv(proc_path, index=False)

        logger.success(f"Saved {len(df)} rows → {raw_path}")
        logger.success(f"Saved {len(df)} rows → {proc_path}")

    return df


def load_feature_df() -> pd.DataFrame:
    """Load the processed feature CSV, generating it if not yet present."""
    proc_path = PROC_DIR / "weekly_features.csv"
    if not proc_path.exists():
        logger.info("Feature CSV not found — generating now …")
        return generate_weekly_features(save=True)
    return pd.read_csv(proc_path, parse_dates=["week_date"])


if __name__ == "__main__":
    df = generate_weekly_features(save=True)
    print(f"\n✅ Generated {len(df)} rows")
    print(df[["week_date", "bpi_5tc", "vlsfo_sgp_usd_t",
              "freight_rate_usd_t", "cyclone_dummy"]].tail(10).to_string())
    print(f"\nFreight rate stats:\n{df['freight_rate_usd_t'].describe()}")
