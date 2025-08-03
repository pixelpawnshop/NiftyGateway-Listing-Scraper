@echo off
echo NiftyGateway Production Scraper - FULL PAGE MODE
echo ================================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the production scraper for FULL PAGE scraping
echo Starting FULL PAGE scrape (this may take 2-4 hours)...
echo Target: ALL available items (~19,000)
echo.

REM Use 0 for unlimited items and high scroll count for full page
python production_scraper.py --max-items 0 --headless --max-scrolls 400

echo.
echo Full page scraping completed. Check the output files for results.
echo Expected: 15,000+ items if successful
pause
