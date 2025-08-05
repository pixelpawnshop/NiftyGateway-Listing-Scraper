@echo off
echo 🚀 Starting Nifty Arbitrage Scanner (Low RAM Mode)

cd /d %~dp0

echo 📊 Starting container with optimized settings...
docker-compose up -d

if %ERRORLEVEL% EQU 0 (
    echo ✅ Scanner started successfully!
    echo.
    echo 📈 Resource monitoring:
    echo   - View logs: docker-compose logs -f
    echo   - Check RAM usage: docker stats
    echo   - Stop scanner: docker-compose down
    echo.
    echo 🎯 Optimized for low RAM usage:
    echo   - Scan interval: 10 minutes
    echo   - Max items: 1000 per scan
    echo   - Reduced scroll attempts
    echo.
    echo 💬 Discord notifications will appear when opportunities are found.
) else (
    echo ❌ Failed to start scanner
    pause
    exit /b 1
)

pause
