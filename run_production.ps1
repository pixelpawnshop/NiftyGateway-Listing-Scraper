# NiftyGateway Production Scraper - PowerShell Version
Write-Host "NiftyGateway Production Scraper" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Run the production scraper with default settings
Write-Host "Starting production scrape..." -ForegroundColor Yellow
python production_scraper.py --max-items 1000 --headless --max-scrolls 50

Write-Host ""
Write-Host "Scraping completed. Check the output files for results." -ForegroundColor Green
Read-Host "Press Enter to continue"
