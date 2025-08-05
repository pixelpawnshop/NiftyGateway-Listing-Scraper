@echo off
echo 🛑 Stopping Nifty Arbitrage Scanner

cd /d %~dp0

echo 📊 Stopping container...
docker-compose down

if %ERRORLEVEL% EQU 0 (
    echo ✅ Scanner stopped successfully!
) else (
    echo ❌ Error stopping scanner
)

pause
