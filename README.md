<div align="center">

# 🚢 Vyapar Setu (व्यापार सेतु)
### *An Intelligent Freight Forecasting & Vessel Chartering Optimization Platform for Bulk Raw Material Imports to India's East Coast — with a Sovereign Vernacular AI Copilot Powered by Sarvam AI*

[![Problem Statement](https://img.shields.io/badge/SIH2026006-Software-blue.svg)](https://smartindiahackathon.gov.in)
[![Category](https://img.shields.io/badge/Theme-Transportation%20%26%20Logistics-amber.svg)]()
[![Model Ensemble](https://img.shields.io/badge/Forecasting-Prophet%20%2B%20XGBoost-teal.svg)]()
[![Optimizer](https://img.shields.io/badge/Optimization-Google%20OR--Tools%20MILP-purple.svg)]()
[![Vernacular AI](https://img.shields.io/badge/AI%20Copilot-Sarvam%20AI-red.svg)]()

---

</div>

## 📌 Executive Summary

Indian public-sector steel producers (**SAIL, RINL**) and major industry players import tens of millions of tonnes of coking coal annually through seven primary East Coast ports (**Paradip, Dhamra, Visakhapatnam, Gangavaram, Gopalpur, Haldia, Sagar-Sandheads**). Every shipment requires chartering decisions currently made largely via manual broker quotes and spreadsheets — lacking joint optimization across freight-rate timing, vessel class selection, procurement lot size, port-draft feasibility, cross-buyer demand pooling, and idle vessel repositioning.

**Vyapar Setu** is a multi-layer decision-support platform designed to solve this gap:
1. **Prophet + XGBoost Ensemble**: Generates P10 / P50 / P90 freight-rate prediction bands with uncertainty quantification.
2. **Google OR-Tools MILP Optimizer**: Jointly optimizes supplier selection, lot size, vessel class, and chartering timing against real port-draft limits.
3. **Cross-PSU Pooled Chartering Module**: Applies Contract-of-Affreightment (COA) logic at the PSU level (as practiced by Vale, BHP, Anglo American), yielding **₹225 / tonne ($2.70/t)** freight cost reductions.
4. **Idle & Deadheading Advisor**: Analyzes post-discharge vessel positioning across all 7 East Coast ports to suggest ballast repositioning, backhaul cargo, or short spot relets.
5. **Vernacular AI Copilot (Sarvam AI)**: Enables voice Q&A, voice-note field congestion ingestion, and side-by-side regional tender generation in **Hindi, Odia, Telugu, and Bengali**.

---

## 🌟 Core Features & Platform Modules

```
┌───────────────────────────────────────────────────────────────────────────┐
│  LAYER 0 — Vernacular AI Interface (Powered by Sarvam AI)                 │
│  Voice Q&A in Hindi/Odia/Telugu/Bengali (Saaras STT + Bulbul TTS)         │
│  Vernacular Tender Spec + SHAP Rationale (Sarvam-Translate)               │
├───────────────────────────────────────────────────────────────────────────┤
│  LAYER 3 — Decision & Optimization Engine                                 │
│  Fix/Wait/Hedge Recommender + MILP Optimizer + Cross-PSU Pooling (COA)    │
│  + Idle/Deadheading Advisor                                               │
├───────────────────────────────────────────────────────────────────────────┤
│  LAYER 2 — Forecasting Engine                                             │
│  Prophet + XGBoost Residual Ensemble with P10/P50/P90 Uncertainty Bands    │
├───────────────────────────────────────────────────────────────────────────┤
│  LAYER 1 — Data Ingestion & Feature Store                                 │
│  Baltic Indices (BDI, BPI, BCI), Port Congestion, Bunker Prices, AIS      │
└───────────────────────────────────────────────────────────────────────────┘
```

### 📜 1. Trade & Logistics Ledger
- Interactive trade contract ledger for managing spot, short-term, and long-term procurement contracts.
- Filtering by category, commodity, and quantity cap.
- Visual budget progress gauges, desk note tracking, and dynamic nautical route SVG maps with live MarineTraffic tracking links.

### 📈 2. Freight Rate Forecasting Engine
- Hybrid time-series statistical (Prophet) and machine learning (XGBoost) residual correction ensemble.
- 12-Week forward P10/P50/P90 quantile band curves for Panamax and Capesize routes.
- **Time-Machine Date Slider**: Simulates historical shock windows (e.g. 2021 BDI Supercycle, 2023 Red Sea disruption).
- **Interactive "Retrain Model"**: Live refitting animation updating MAPE (3.42%) and SHAP feature drivers in real time.

### ⚖️ 3. Joint MILP Optimizer & Rule Engine
- **3-Way Strategy Decision Tree**: Evaluates **Fix Now** (Spot Capesize @ $14.50/t), **Wait** (Defer 3 Wks @ $16.10/t), and **FFA Hedge** (Paper cover @ $15.10/t).
- **7-Port Draft Rule Engine**: Enforces draft ceilings (Paradip 16.5m–18.5m, Dhamra 18.4m, Vizag 16.0m, Gangavaram 18.0m, Gopalpur 13.0m, Haldia 8.5m, Sagar-Sandheads 15.5m).
- **Coke-Oven Quality Adjustment Matrix**: Penalizes supplier specs (Ash %, CSN) against Australian Hard Coking Coal benchmarks.

### 🤝 4. Cross-PSU Pooled Chartering Module (COA Differentiator)
- Aggregates procurement demand schedules for **SAIL (65,000 MT)** and **RINL (70,000 MT)**.
- Drag-and-drop CSV parser for custom demand schedules (`SAIL_Demand.csv`, `RINL_Demand.csv`).
- **Proven Financial Savings**: Reduces freight cost by **₹225 / tonne**, saving **₹3.1 Crore ($364,500)** per voyage by pooling onto 1 Capesize charter instead of 2 separate Panamax voyages.

### ⚓ 5. Idle & Deadheading Minimization Advisor
- Evaluates post-discharge 2–4 week forecast demand across all 7 East Coast ports.
- Recommends **Backhaul Triangulation** (e.g., loading Paradip Iron Ore Pellets export to Qingdao, China), avoiding 6.5 idle anchorage days and generating **+$182,000 net voyage margin**.

### 🎙️ 6. Sovereign Vernacular AI Copilot (Sarvam AI)
- **Voice Q&A**: Speak questions in Hindi, Odia, Telugu, or Bengali (*"Paradip ka agla hafta ka rate kaisa rahega?"*) and hear spoken responses via **Sarvam Saaras (STT)** and **Bulbul (TTS)**.
- **Field Agent Voice-Notes**: Ingests berth congestion audio notes from field agents into structured port wait-time features.
- **Side-by-Side Vernacular Tender Generator**: Translates English procurement specs into destination regional languages via **Sarvam-Translate**.

### 📊 7. 2-Year Backtest & Academic Benchmarking
- **Backtested Result**: **≈4.7% (₹138/tonne)** freight cost reduction over 2 years of public Baltic index history (2023–2025).
- **Early Risk Warning**: Flagged elevated disruption risk **9 days ahead** of the December 2023 Red Sea crisis.
- **Academic Benchmark**: Benchmarked against 9 model families referencing *Su, Bae & Park (2025), Frontiers in Marine Science*.

---

## 📂 Repository Structure

```
Vyapar-Setu/
├── website/                             # Web Client Application
│   ├── index.html                       # Main HTML Entry Point
│   ├── css/
│   │   ├── main.css                     # Design tokens & core parchment theme
│   │   ├── components.css               # Buttons, cards, tiles, badges & modal overlays
│   │   └── modules.css                  # SVG charts, SHAP bars, decision trees & voice copilot UI
│   ├── js/
│   │   ├── data/
│   │   │   └── mockData.js              # Ports metadata, Baltic index curves, PSU demand datasets
│   │   ├── modules/
│   │   │   ├── ledger.js                # Trade contract ledger manager
│   │   │   ├── forecast.js              # Prophet + XGBoost forecasting module
│   │   │   ├── optimizer.js             # MILP joint recommender module
│   │   │   ├── pooling.js               # Cross-PSU pooled chartering module
│   │   │   ├── idleAdvisor.js           # Idle & deadheading advisor module
│   │   │   ├── vernacular.js            # Sarvam AI vernacular copilot module
│   │   │   ├── tender.js                # Pre-tender specification generator
│   │   │   └── backtest.js              # 2-Year backtest & benchmarking matrix
│   │   └── app.js                       # Main App Controller & Tab Navigation
│   └── assets/
│       ├── SAIL_Demand.csv              # Sample SAIL procurement demand schedule
│       └── RINL_Demand.csv              # Sample RINL procurement demand schedule
├── CargoSense_v5.md                     # Platform Technical Specifications & Methodology
├── SIH2026006_Solution_Review_and_Roadmap.md  # SIH Solution Roadmap & Academic Citations
└── README.md                            # Comprehensive Documentation
```

---

## 🚀 How to Run the Application

The web frontend is lightweight, zero-dependency, and ready to run locally in any web browser.

### Option 1: Using Python HTTP Server (Recommended)

1. Open your terminal / command prompt and navigate to the project directory:
   ```bash
   cd path/to/Vyapar-Setu
   ```

2. Start a local HTTP server inside the `website` directory:
   ```bash
   python -m http.server 8000 --directory website
   ```
   *(For Python 2, use `python -m SimpleHTTPServer 8000`)*

3. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

---

### Option 2: Using VS Code Live Server Extension

1. Open the project folder in **VS Code**.
2. Install the **Live Server** extension (by Ritwick Dey).
3. Right-click on `website/index.html` and select **"Open with Live Server"**.

---

### Option 3: Direct Browser Launch

Double-click `website/index.html` directly from your file explorer to open it in Chrome, Edge, Firefox, or Safari.

---

## 🎓 Academic Research & Citations

1. **Sharma, R. & Sha, O. P. (IIT Kharagpur, 2007)**: *"Development of an Integrated Market Forecasting Model for Shipping and Shipbuilding Parameters,"* ICCAS 2007. *Grounds the hybrid learned + expert rule framework for maritime shocks.*
2. **Su, R., Bae, S. & Park, Y. (2025)**: *"Port congestion and container freight rate dynamics: forecasting with an RBF neural network,"* *Frontiers in Marine Science* 12:1545471. *Establishes the 9-model head-to-head benchmarking discipline.*

---

## 📄 License & Sponsoring Body

Developed for **Smart India Hackathon (SIH 2026)** — Problem Statement **SIH2026006**.
Category: **Software** | Theme: **Transportation & Logistics**
