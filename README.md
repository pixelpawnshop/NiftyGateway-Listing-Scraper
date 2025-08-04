# NiftyGateway NFT Floor Price Scraper

A comprehensive Python-based web scraper designed to extract floor price data from NiftyGateway's marketplace.

## 🎯 Purpose

This scraper was built to **pull floor listing prices on NiftyGateway**

## ✨ Features

- **Full Page Scraping**: Captures all ~19,000 available NFT collections
- **Two-Phase Approach**: Efficiently collects URLs first, then processes floor price data
- **OpenSea Integration**: Automatically enriches data with collection names and slugs for cross-platform analysis
- **Real-Time Arbitrage Analysis**: Fetches top offers from OpenSea and calculates profit opportunities
- **Smart Flagging System**: 3-tier color-coded system for arbitrage opportunities (Red/Yellow/Green)
- **Live ETH Price Updates**: Automatically updates ETH/USD price every minute for accurate calculations
- **Robust Error Handling**: Gracefully handles network issues, timeouts, and page load failures
- **Progress Tracking**: Real-time progress updates with success/failure statistics
- **Interruption-Safe**: Can be stopped anytime with Ctrl+C while preserving partial results
- **Multiple Output Formats**: Saves data in both JSON and CSV formats
- **Clean Data Structure**: Outputs only essential fields for arbitrage analysis
- **Production Ready**: Optimized for headless operation and long-running processes
- **Smart Filtering**: Only scrapes items with actual listings (skips items with no List Price)
- **Offer-Only Mode**: When arbitrage analysis is enabled, only saves items with active OpenSea offers for clean output

## 📊 Output Data Structure

The scraper extracts the following comprehensive data for each collection:

```json
{
  "floor_price": 1736.13,
  "floor_price_text": "$1736.13 (Table List Price)",
  "contract": "0x4a524d236760d918993ccfb8675c7e35e9a767a6",
  "actual_token_id": "100000100012",
  "marketplace_url": "https://www.niftygateway.com/marketplace/collection/0x4a524d236760d918993ccfb8675c7e35e9a767a6/1/",
  "actual_marketplace_url": "https://www.niftygateway.com/marketplace/item/0x4a524d236760d918993ccfb8675c7e35e9a767a6/100000100012/",
  "collection_name": "XCOPY",
  "collection_slug": "select-works-by-xcopy",
  "opensea_enriched_at": "2025-08-04T16:27:01.123456",
  "opensea_collection_url": "https://opensea.io/collection/select-works-by-xcopy",
  "opensea_item_url": "https://opensea.io/assets/ethereum/0x4a524d236760d918993ccfb8675c7e35e9a767a6/100000100012",
  "opensea_offer_data": {
    "offer_amount_wei": "2000000000000000000",
    "offer_amount_eth": 2.0,
    "offer_amount_usd": 7100.0,
    "total_offer_wei": "10000000000000000000",
    "quantity": 5,
    "order_hash": "0x5bc9ff0f7fa56c6694f801e17fa08a87f73f612754020ba61006301c7afaf453",
    "fetched_at": "2025-08-04T16:27:02.456789"
  },
  "arbitrage_flag": "🔥 RED",
  "arbitrage_description": "OpenSea offer >= Nifty price - EXCELLENT arbitrage (instant profit)",
  "profit_percentage": 1742.5,
  "potential_profit_usd": 30254.42,
  "arbitrage_analyzed_at": "2025-08-04T16:27:02.789012",
  "scraped_at": "2025-08-03T18:20:59.111937"
}
```

### OpenSea Integration

The scraper automatically enriches each item with OpenSea collection data:
- **collection_name**: Human-readable collection name from OpenSea
- **collection_slug**: OpenSea collection identifier for building URLs
- **opensea_collection_url**: Direct link to the collection page on OpenSea
- **opensea_item_url**: Direct link to the specific NFT item on OpenSea
- **opensea_enriched_at**: Timestamp when OpenSea data was fetched

### Arbitrage Analysis

Real-time arbitrage opportunity detection with 3-tier flagging system and multi-quantity offer support:

**Important**: When arbitrage analysis is enabled, the scraper automatically filters out items with no OpenSea offers to keep the output clean and focused on actual opportunities.

#### Multi-Quantity Offer Handling
- **Automatic Detection**: Identifies ERC-1155 multi-item offers (itemType 4)
- **Per-Item Pricing**: Divides total offer amount by quantity for accurate per-item comparison
- **Quantity Display**: Shows both per-item price and total quantity (e.g., "5x quantity")
- **Accurate Analysis**: Ensures arbitrage calculations are based on actual per-item values

#### 🔥 RED FLAG - EXCELLENT Arbitrage
- OpenSea offer >= NiftyGateway listing price
- **Instant profit potential** - buy on Nifty, sell offer on OpenSea

#### 🟡 YELLOW FLAG - GOOD Arbitrage  
- OpenSea offer within 10% of NiftyGateway price
- **Strong arbitrage potential** with minimal risk

#### 🟢 GREEN FLAG - FAIR Arbitrage
- OpenSea offer within 20% of NiftyGateway price  
- **Moderate arbitrage potential** for experienced traders

#### ⚪ WHITE FLAG - LIMITED Arbitrage
- OpenSea offer more than 20% below NiftyGateway price
- **Low arbitrage potential**

#### ⚫ NO_OFFER - No Market
- No active offers found on OpenSea
- **No current arbitrage opportunity**

This enables immediate identification of profitable cross-platform trading opportunities.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- Chrome browser installed
- Windows OS (batch files provided for Windows)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pixelpawnshop/nifty_listing_scraper.git
   cd nifty_listing_scraper
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Scraper

#### Option 1: Full Page Scraping (Recommended)
For capturing all ~19,000 collections:

**PowerShell**:
```powershell
.\run_production.ps1
```

**Command Prompt**:
```cmd
.\run_production.bat
```

#### Option 2: Manual Execution
```bash
# Activate environment
venv\Scripts\activate

# Run full page scrape with output to output\ folder
python src\production_scraper.py --max-items 0 --headless --max-scrolls 400 --output-dir output
```

#### Option 3: Custom Parameters
```bash
python src\production_scraper.py --max-items 1000 --max-scrolls 100 --headless --output-dir output
```

## ⚙️ Configuration Options

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--max-items` | Max items to scrape (0 = unlimited) | 1000 | `--max-items 0` |
| `--headless` | Run without browser window | False | `--headless` |
| `--max-scrolls` | Maximum scroll attempts | 50 | `--max-scrolls 400` |
| `--output-dir` | Output directory for files | Current dir | `--output-dir ./data` |

## 📈 Performance Expectations

### Full Page Scraping (~19,000 items):
- **Duration**: 3-4 hours
- **Scroll attempts**: ~400 (50 items per scroll)
- **Success rate**: 85-95% typical
- **Output files**: 2 files (JSON + CSV) with timestamp

### Sample Scraping (1,000 items):
- **Duration**: 15-20 minutes
- **Scroll attempts**: ~20
- **Perfect for testing and development

## 📁 Project Structure

```
niftyscraper/
├── src/                      # Source code directory
│   ├── nifty_scraper.py         # Main scraper class with all logic
│   ├── production_scraper.py    # CLI interface for production use
│   ├── opensea_client.py        # OpenSea collection data integration
│   ├── opensea_offers_client.py # OpenSea offers and arbitrage analysis
│   ├── config.py                # Configuration settings
│   └── run_production.bat       # Alternative batch file (run from src/)
├── output/                   # Output directory for generated files
│   ├── nifty_gateway_items_[timestamp].json  # JSON results
│   └── nifty_gateway_items_[timestamp].csv   # CSV results
├── requirements.txt          # Python dependencies
├── run_production.bat        # Main Windows batch file for full scraping
├── run_production.ps1        # PowerShell script for full scraping
├── venv/                     # Virtual environment
└── README.md                 # This file
```

## 🛠️ Technical Details

### Architecture
- **Phase 1**: Aggressive scrolling to collect all collection URLs
- **Phase 2**: Sequential processing of each URL to extract floor price data
- **Selenium WebDriver**: Automated Chrome browser interaction
- **Multiple Scroll Strategies**: Ensures maximum content discovery

### Error Handling
- **Navigation Retries**: Failed page loads are retried automatically
- **Graceful Degradation**: Continues scraping even if individual items fail
- **Partial Result Preservation**: Saves progress if interrupted
- **Comprehensive Logging**: Detailed progress and error reporting

### Anti-Detection Measures
- **Human-like Scrolling**: Multiple small scrolls to simulate user behavior
- **Random Delays**: Variable wait times between requests
- **Standard User Agent**: Mimics regular Chrome browser

## 📊 Sample Output Files

After scraping, you'll find timestamped files like:
- `nifty_gateway_items_20250803_181317.json`
- `nifty_gateway_items_20250803_181317.csv`

## 🔧 Troubleshooting

### Common Issues

**PowerShell Execution Policy Error**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**ChromeDriver Issues**:
- The scraper auto-downloads compatible ChromeDriver
- Ensure Chrome browser is updated to latest version

**Memory Issues (Large Scrapes)**:
- Close other applications
- Use `--headless` flag to reduce memory usage
- Consider running overnight with fewer concurrent applications

### Performance Optimization

**For Maximum Speed**:
- Use `--headless` flag
- Close unnecessary applications
- Ensure stable internet connection
- Run during off-peak hours

**For Maximum Reliability**:
- Reduce `--max-scrolls` and run multiple smaller batches
- Monitor progress and restart if needed
- Use wired internet connection

## 📝 Development

### Adding New Features
The scraper is modular and extensible:
- **nifty_scraper.py**: Core scraping logic
- **production_scraper.py**: CLI interface
- **config.py**: Settings and URLs

### Testing
```bash
# Test with small dataset
python production_scraper.py --max-items 10 --max-scrolls 5
```

## ⚠️ Important Notes

### Rate Limiting
- Built-in delays prevent overwhelming the server
- Respect NiftyGateway's terms of service
- Use responsibly for legitimate research purposes

### Data Accuracy
- Floor prices are extracted from the "List Price" column
- Data reflects the cheapest available item per collection
- Prices are in USD as displayed on NiftyGateway

### Legal Compliance
- This tool is for educational and research purposes
- Ensure compliance with NiftyGateway's terms of service
- Use scraped data responsibly and ethically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please ensure compliance with all applicable terms of service and legal requirements.

## 📞 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**Happy scraping! 🚀**

*Remember: This tool is designed for legitimate arbitrage research. Please use responsibly and in compliance with all applicable terms of service.*
