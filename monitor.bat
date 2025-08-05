@echo off
setlocal enabledelayedexpansion
echo Nifty Arbitrage Scanner - Health Monitor

cd /d %~dp0

:monitor_loop
echo === Health Check at %time% ===

REM Check if container is running
docker-compose ps | findstr "Up" > nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Container is not running - attempting restart...
    call discord_alert.bat "ERROR: Scanner OFFLINE - Attempting restart"
    docker-compose up -d
    timeout /t 30 > nul
    goto monitor_loop
)

REM Check for Chrome crashes in recent logs
docker-compose logs --tail=50 | findstr "tab crashed" > nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Chrome crashes detected - restarting container...
    call discord_alert.bat "WARNING: Chrome crashes detected - Restarting scanner"
    docker-compose restart
    timeout /t 60 > nul
)

REM Check memory usage
for /f "skip=1 tokens=3" %%i in ('docker stats --no-stream --format "table {{.MemPerc}}" nifty-arbitrage-scanner 2^>nul') do (
    set mem_usage=%%i
    goto :check_memory
)

:check_memory
if defined mem_usage (
    set /a mem_num=0
    for /f "tokens=1 delims=%%" %%a in ("%mem_usage%") do set /a mem_num=%%a
    if !mem_num! GTR 80 (
        echo WARNING: High memory usage: %mem_usage%
        call discord_alert.bat "WARNING: High memory usage: %mem_usage% - Monitor scanner"
    )
)

REM Check for completely stuck scanning (no progress in logs for 12 hours - only restart if truly dead)
docker-compose logs --since=12h | findstr /c:"Processing" /c:"Scroll attempt" /c:"Found" /c:"URLs" /c:"WebDriver setup" /c:"Starting arbitrage scan" > nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: No scanning activity in 12 hours - scanner may be dead - restarting...
    call discord_alert.bat "WARNING: Scanner appears completely dead (12h no activity) - Restarting"
    docker-compose restart
    timeout /t 60 > nul
) else (
    echo INFO: Scanner is active - scan in progress, not interrupting
)

echo SUCCESS: Health check passed at %time%
timeout /t 300 > nul
goto monitor_loop
