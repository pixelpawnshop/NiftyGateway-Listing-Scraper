# NiftyGateway Production Scraper - PowerShell Version (FULL PAGE MODE)
Write-Host "NiftyGateway Production Scraper - FULL PAGE MODE" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please make sure you're in the correct directory and the venv folder exists." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
try {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting FULL PAGE scrape (this may take 2-4 hours)..." -ForegroundColor Yellow
Write-Host "🎯 Target: ALL available items (~19,000)" -ForegroundColor Yellow
Write-Host "🔗 OpenSea enrichment: ENABLED (collection names & slugs)" -ForegroundColor Cyan
Write-Host "💎 Arbitrage analysis: ENABLED (real-time opportunity detection)" -ForegroundColor Cyan
Write-Host "📁 Output directory: output\" -ForegroundColor Cyan
Write-Host ""

# Run the scraper with full page settings and OpenSea enrichment
try {
    python src\production_scraper.py --max-items 0 --headless --max-scrolls 400 --output-dir output
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "✅ Full page scraping completed successfully!" -ForegroundColor Green
        Write-Host "📁 Check the output\ folder for results." -ForegroundColor Cyan
        Write-Host "📊 Expected: 15,000+ items if successful" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  Scraping completed with errors (exit code: $exitCode)" -ForegroundColor Yellow
        Write-Host "📁 Check the output\ folder for partial results." -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Error running scraper: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue"
