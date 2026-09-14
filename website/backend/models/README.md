# Vyapar Setu — Trained Model Artifacts
# This folder stores pickled ML model files generated during training.
#
# Files:
#   prophet_model.pkl      — Trained Prophet base model
#   xgb_model.pkl          — Trained XGBoost residual corrector
#   scaler.pkl             — StandardScaler for feature normalization
#   residual_stats.pkl     — P10/P90 quantiles from training residuals
#   metrics.pkl            — Backtest metrics (MAPE, RMSE, savings)
#   training_df.csv        — Training data with predictions for backtest
#
# Models are trained automatically on first API request.
# To manually train:
#   cd website/backend
#   python services/forecaster.py
