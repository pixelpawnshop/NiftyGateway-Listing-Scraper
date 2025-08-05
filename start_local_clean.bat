@echo off
echo Starting Nifty Arbitrage Scanner with Health Monitoring

cd /d %~dp0

REM Start the main scanner
echo Starting container with optimized settings...
docker-compose up -d

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Scanner started successfully!
    
    REM Send startup notification
    call discord_alert.bat "SUCCESS: Arbitrage Scanner STARTED - Monitoring active"
    
    echo.
    echo Starting health monitor in new window...
    start "Scanner Health Monitor" monitor.bat
    
    echo.
    echo Management commands:
    echo   - View logs: docker-compose logs -f
    echo   - Check RAM usage: docker stats
    echo   - Stop everything: stop_all.bat
    echo.
    echo Monitoring features active:
    echo   - Chrome crash detection and restart
    echo   - Memory usage alerts (greater than 80 percent)
    echo   - Dead scanner detection (12 hour timeout - will NOT interrupt scans)
    echo   - Discord health notifications
    echo.
    echo FULL MARKETPLACE SCAN MODE:
    echo   - 400 scroll attempts (~19,000 items)
    echo   - URL collection: ~1-2 hours
    echo   - Arbitrage analysis: ~4-8 hours (depends on network/API speed)
    echo   - Total scan time: ~6-10 hours per complete cycle
    echo   - Scanner will COMPLETE each full scan before restarting
    echo.
    echo Both arbitrage opportunities AND health alerts will appear in Discord.
    pause
    exit /b 0
) else (
    echo ERROR: Failed to start scanner
    call discord_alert.bat "ERROR: FAILED to start Arbitrage Scanner"
    pause
    exit /b 1
)