# 🚢 Vyapar Setu Web Application

This folder contains the complete, ready-to-run web client application for **Vyapar Setu** (formerly CargoSense v5).

## 🚀 Quick Start Guide

### Running Locally with Python
```bash
# Navigate to the repository root or website directory
python -m http.server 8000 --directory website
```
Then visit **`http://localhost:8000`** in your browser.

---

## 📁 File Structure

- `index.html`: Main HTML entry point & multi-tab navigation container.
- `css/main.css`: Core design system, parchment vintage palette tokens, base reset.
- `css/components.css`: Buttons, cards, badges, tiles, budget gauges, modal overlays, toast notifications.
- `css/modules.css`: Module layouts (forecast SVG chart, SHAP bars, decision tree grid, voice copilot widget).
- `js/data/mockData.js`: Ports metadata across 7 East Coast ports, Baltic indices, PSU demand datasets, Sarvam voice samples.
- `js/modules/`: Individual ES6 functional UI modules:
  - `ledger.js`: Contract management ledger & detail inspector.
  - `forecast.js`: Prophet + XGBoost ensemble forecast & SHAP explainability.
  - `optimizer.js`: MILP solver 3-way strategy recommender (Fix/Wait/Hedge).
  - `pooling.js`: Cross-PSU Contract of Affreightment (COA) pooling parser.
  - `idleAdvisor.js`: Post-discharge idle/deadheading advisor.
  - `vernacular.js`: Sarvam AI voice copilot & voice note ingestion.
  - `tender.js`: Pre-tender specification generator & regional translators.
  - `backtest.js`: 2-Year historical backtest & academic benchmark suite.
- `js/app.js`: Main application controller.
- `assets/`: Sample demand files (`SAIL_Demand.csv`, `RINL_Demand.csv`).
