@echo off
title VANET Anomaly Detection System
color 0A

echo ================================================
echo    VANET ANOMALY DETECTION SYSTEM
echo    Capstone Project
echo ================================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo       Python OK

echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo       Node.js OK

echo.
echo ================================================
echo    Starting Backend Server (FastAPI)
echo ================================================
echo.

if exist "%~dp0backend\main.py" (
    start "VANET Backend" cmd /k "cd /d "%~dp0backend" && pip install -r requirements.txt && echo. && echo Backend starting at http://localhost:8000 && echo. && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo ERROR: Cannot find backend\main.py
    pause
    exit /b 1
)

echo Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ================================================
echo    Starting Frontend Server (React + Vite)
echo ================================================
echo.

if exist "%~dp0client\package.json" (
    start "VANET Frontend" cmd /k "cd /d "%~dp0client" && npm install && echo. && echo Frontend starting at http://localhost:5173 && echo. && npm run dev"
) else (
    echo ERROR: Cannot find client\package.json
    pause
    exit /b 1
)

echo.
echo ================================================
echo    SYSTEM LAUNCHING
echo ================================================
echo.
echo    Backend API:  http://localhost:8000
echo    Frontend UI:  http://localhost:5173
echo    API Docs:     http://localhost:8000/docs
echo.
echo    Opening browser in 10 seconds...
echo.
echo ================================================

timeout /t 10 /nobreak >nul

start http://localhost:5173

echo.
echo Press any key to close this window...
echo (The servers will continue running in their windows)
pause >nul
