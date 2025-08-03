@echo off
echo NiftyGateway Production Scraper
echo ================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the production scraper with default settings
echo Starting production scrape...
python production_scraper.py --max-items 1000 --headless --max-scrolls 50

echo.
echo Scraping completed. Check the output files for results.
pause
