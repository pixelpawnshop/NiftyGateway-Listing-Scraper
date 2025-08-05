@echo off
echo 🛑 Stopping Nifty Arbitrage Scanner and Monitoring

cd /d %~dp0

REM Kill monitor window
taskkill /f /fi "WindowTitle eq Scanner Health Monitor*" > nul 2>&1

echo 📊 Stopping container...
docker-compose down

if %ERRORLEVEL% EQU 0 (
    echo ✅ Scanner and monitoring stopped successfully!
    call discord_alert.bat "🛑 Arbitrage Scanner STOPPED - Monitoring disabled"
) else (
    echo ❌ Error stopping scanner
)

pause
