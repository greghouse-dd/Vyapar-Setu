@echo off
REM ================================================================
REM  Vyapar Setu — Backend Startup Script
REM  Run from: website/backend/
REM ================================================================

echo.
echo  ██╗   ██╗██╗   ██╗ █████╗ ██████╗  █████╗ ██████╗     ███████╗███████╗████████╗██╗   ██╗
echo  ██║   ██║╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗    ██╔════╝██╔════╝╚══██╔══╝██║   ██║
echo  ██║   ██║ ╚████╔╝ ███████║██████╔╝███████║██████╔╝    ███████╗█████╗     ██║   ██║   ██║
echo  ╚██╗ ██╔╝  ╚██╔╝  ██╔══██║██╔═══╝ ██╔══██║██╔══██╗    ╚════██║██╔══╝     ██║   ██║   ██║
echo   ╚████╔╝    ██║   ██║  ██║██║     ██║  ██║██║  ██║    ███████║███████╗   ██║   ╚██████╔╝
echo    ╚═══╝     ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚══════╝   ╚═╝    ╚═════╝
echo.
echo  SIH 2026 ^| FastAPI Backend ^| Port 8001
echo  ================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Install requirements if venv not activated
if not exist ".venv" (
    echo [SETUP] Creating virtual environment...
    python -m venv .venv
    echo [SETUP] Installing dependencies (this may take a few minutes)...
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

REM Copy .env if needed
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [CONFIG] Created .env from template. Edit .env to add SARVAM_API_KEY.
    )
)

REM Generate data if not present
if not exist "data\raw\freight_rates.csv" (
    echo [DATA] Generating synthetic dataset...
    python services\data_pipeline.py
)

REM Initialize database
echo [DB] Initializing database...
python -m db.init_db

REM Start server
echo.
echo [START] Starting Vyapar Setu API on http://localhost:8001
echo         Swagger UI: http://localhost:8001/docs
echo         Press Ctrl+C to stop
echo.
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
