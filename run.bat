@echo off
setlocal
title Sentinel AI - Autonomous Real-Time Big Data Engine
cd /d "%~dp0"

echo =====================================================================
echo    SENTINEL-AI // Autonomous Real-Time Big Data Engine
echo =====================================================================
echo.

:: 1. Verify Python is installed and in PATH
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    echo or run using Docker: docker compose up --build
    echo.
    pause
    exit /b 1
)

:: 2. Install / Verify Dependencies
echo [1/2] Checking and verifying dependencies...
python -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pip dependency check had warnings, attempting to proceed...
)

:: 3. Launch Streamlit Application
echo [2/2] Launching Sentinel AI Dashboard on http://localhost:8501...
echo.
echo Close this window to stop the application.
echo =====================================================================
echo.

:: Launch Streamlit
python -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)
