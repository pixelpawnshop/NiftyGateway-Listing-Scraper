@echo off
echo 📊 Nifty Arbitrage Scanner - Status & Logs

cd /d %~dp0

echo === Container Status ===
docker-compose ps
echo.

echo === Resource Usage ===
docker stats --no-stream nifty-arbitrage-scanner 2>nul
echo.

echo === Recent Logs (Last 20 lines) ===
docker-compose logs --tail=20
echo.

echo === Commands ===
echo View live logs: docker-compose logs -f
echo Restart: docker-compose restart
echo Stop: docker-compose down
echo.

pause
