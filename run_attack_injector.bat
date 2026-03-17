@echo off
REM VANET Attack Injector - Quick Launch Script
REM This script runs the attack injector with common configurations

:start
cls
echo ============================================================
echo VANET Attack Injector - Quick Launch
echo ============================================================
echo.
echo IMPORTANT: Make sure backend is running on http://localhost:8000
echo.
echo Select mode:
echo 1. Quick Test (30 seconds)
echo 2. Medium Test (60 seconds)
echo 3. Long Test (120 seconds)
echo 4. Continuous Mode (until Ctrl+C)
echo 5. Custom Configuration
echo 6. Test Connection
echo 7. Exit
echo.
set /p choice="Enter choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Running 30-second attack campaign...
    echo.
    python attack_injector.py --duration 30
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running 60-second attack campaign...
    echo.
    python attack_injector.py --duration 60
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Running 120-second attack campaign...
    echo.
    python attack_injector.py --duration 120
    goto end
)

if "%choice%"=="4" (
    echo.
    echo ============================================================
    echo CONTINUOUS MODE - Press Ctrl+C to stop
    echo ============================================================
    echo.
    echo Starting continuous attack mode with 5-second intervals...
    echo The script will run until you press Ctrl+C
    echo.
    python attack_injector.py --continuous --interval 5
    goto end
)

if "%choice%"=="5" (
    echo.
    set /p duration="Enter duration in seconds: "
    set /p interval="Enter interval between attacks: "
    echo.
    echo Running custom configuration...
    echo.
    python attack_injector.py --duration %duration% --interval %interval%
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Testing connection to backend...
    echo.
    curl -s http://localhost:8000/ 2>nul
    if errorlevel 1 (
        echo.
        echo ❌ Backend is NOT running!
        echo Please start backend first:
        echo    cd backend
        echo    python -m uvicorn main:app --reload --port 8000
    ) else (
        echo.
        echo ✓ Backend is running and accessible!
        echo ✓ You can now run the attack injector.
        echo.
        echo Note: The attack injector will:
        echo   1. Login with admin credentials
        echo   2. Enable attack mode
        echo   3. Start injecting attacks
        echo   4. Dashboard will detect them in real-time
    )
    echo.
    echo Press any key to return to menu...
    pause >nul
    cls
    goto :start
)

if "%choice%"=="7" (
    echo.
    echo Exiting...
    goto :eof
)

echo Invalid choice!
pause
goto :start

:end
echo.
echo ============================================================
echo Attack injector finished!
echo ============================================================
echo.
echo Press any key to return to menu or close window to exit...
pause >nul
goto :start
