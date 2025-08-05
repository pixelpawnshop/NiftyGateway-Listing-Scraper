@echo off
REM Send Discord alert for monitoring issues
set message=%~1
set webhook_url=https://discord.com/api/webhooks/1401964079651754076/dQVdnPAIdyBI4NUIh8ISmJr7uGqp4-Hhk264Y5y8j5IqfK-I_V9PzA7yAmGA8WDVcv2k

REM Create JSON payload
echo {"content": "🤖 **Arbitrage Scanner Status**\n%message%\nTime: %date% %time%"} > temp_alert.json

REM Send to Discord using curl (if available)
curl -H "Content-Type: application/json" -X POST -d @temp_alert.json %webhook_url% > nul 2>&1

REM If curl fails, try PowerShell
if %ERRORLEVEL% NEQ 0 (
    powershell -Command "Invoke-RestMethod -Uri '%webhook_url%' -Method Post -ContentType 'application/json' -Body (Get-Content temp_alert.json -Raw)" > nul 2>&1
)

REM Cleanup
del temp_alert.json > nul 2>&1
