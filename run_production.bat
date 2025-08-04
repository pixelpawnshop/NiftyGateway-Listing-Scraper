@echo off
echo 🤖 NiftyGateway Arbitrage Scanner - Discord Alert Mode
echo ================================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the arbitrage scanner with Discord notifications
echo 🚀 Starting arbitrage opportunity scanner...
echo 🎯 Target: ALL available items (~19,000)
echo 📊 OpenSea enrichment: ENABLED (collection names ^& slugs)
echo 💎 Arbitrage analysis: ENABLED (real-time opportunity detection)
echo 💬 Discord alerts: ENABLED for 🔥 RED, 🟡 YELLOW, 🟢 GREEN opportunities
echo ⚡ Mode: Continuous scanning
echo.

REM Run continuous scanning with Discord notifications
python src\production_scraper.py --max-items 0 --headless --max-scrolls 400 --continuous

echo.
echo 🔧 Arbitrage scanner stopped.

pause
