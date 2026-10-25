@echo off
setlocal
title Sentinel AI - Docker Launcher
cd /d "%~dp0"

echo =====================================================================
echo    SENTINEL-AI // Docker Containerized Launcher
echo =====================================================================
echo.

:: 1. Verify Docker is available and running
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker command not found.
    echo Please install Docker Desktop from https://www.docker.com/
    echo or run natively via run.bat
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running!
    echo Please open Docker Desktop and wait for the engine to start,
    echo then run this script again or run natively via run.bat.
    echo.
    pause
    exit /b 1
)

:: 2. Build and start containers
echo Building and starting Sentinel AI container...
echo Dashboard will be available at: http://localhost:8501
echo.
docker compose up --build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Docker compose encountered an error.
    pause
)
