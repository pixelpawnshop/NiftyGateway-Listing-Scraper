# NiftyGateway Real-Time Arbitrage Scanner

A sophisticated real-time arbitrage detection system that monitors NiftyGateway NFT marketplace and sends instant Discord notifications for profitable trading opportunities.

## 🎯 Purpose

This scanner was built to **identify arbitrage opportunities between NiftyGateway and OpenSea in real-time** with instant Discord alerts for time-sensitive trading opportunities.

## ✨ Features

- **Real-Time Arbitrage Detection**: Instant Discord notifications the moment profitable opportunities are found
- **Cross-Platform Analysis**: Compares NiftyGateway list prices with OpenSea top offers in real-time  
- **Smart Flagging System**: 3-tier color-coded system (🔥 RED, 🟡 YELLOW, 🟢 GREEN) for opportunity prioritization
- **Live ETH Price Updates**: Automatically updates ETH/USD price every minute for accurate profit calculations
- **Multi-Quantity Offer Support**: Handles ERC-1155 multi-item offers with accurate per-item pricing
- **Continuous Monitoring**: Optional continuous scanning mode for 24/7 opportunity detection
- **Instant Discord Alerts**: Rich embed notifications with direct buy/sell links and profit calculations
- **Production Ready**: Headless operation optimized for VPS deployment
- **Robust Error Handling**: Gracefully handles network issues and API rate limits
- **Smart Filtering**: Only processes items with actual listings and active OpenSea offers

## 📊 Discord Notification System

The scanner sends rich Discord embed notifications instantly when arbitrage opportunities are discovered:

### Example Discord Alert:
```
🔥 RED ARBITRAGE OPPORTUNITY

XCOPY #100000100012
💰 Profit: +$2,254.42 (+65.2%)

📈 NiftyGateway: $1,736.13
📊 OpenSea Offer: 2.0000 ETH ($3,650.00)

🚀 INSTANT PROFIT - OpenSea offer >= Nifty price!

🛒 Buy on NiftyGateway → 💎 Sell on OpenSea
```

### Notification Features:
- **Instant Alerts**: Fired immediately when opportunity is found (not at scan end)
- **Rich Embeds**: Color-coded with profit calculations and direct links
- **Profit Analysis**: Shows exact USD profit and percentage gain
- **Direct Links**: One-click access to buy on NiftyGateway and sell on OpenSea
- **Collection Info**: OpenSea collection links for additional research

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

Real-time arbitrage opportunity detection with instant Discord notifications:

#### 🔥 RED FLAG - EXCELLENT Arbitrage
- OpenSea offer >= NiftyGateway listing price
- **Instant profit potential** - buy on Nifty, sell offer on OpenSea
- **Immediate Discord alert** with profit calculations

#### 🟡 YELLOW FLAG - GOOD Arbitrage  
- OpenSea offer within 10% of NiftyGateway price
- **Strong arbitrage potential** with minimal risk
- **Real-time notification** for quick action

#### 🟢 GREEN FLAG - FAIR Arbitrage
- OpenSea offer within 20% of NiftyGateway price  
- **Moderate arbitrage potential** for experienced traders
- **Instant alert** for opportunity awareness

This enables immediate identification and action on profitable cross-platform trading opportunities.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- Chrome browser installed  
- Discord webhook URL for notifications
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

4. **Configure Discord webhook**:
   - Update the `DISCORD_WEBHOOK_URL` in `src/production_scraper.py`
   - Test webhook with a small scan first

### Running the Arbitrage Scanner

#### Option 1: Continuous Monitoring (Recommended)
For 24/7 arbitrage opportunity detection:

**PowerShell**:
```powershell
.\run_production.ps1
```

**Command Prompt**:
```cmd
.\run_production.bat
```

#### Option 2: Single Scan
```bash
# Activate environment
venv\Scripts\activate

# Run single scan with real-time Discord alerts
python src\production_scraper.py --max-items 0 --headless --max-scrolls 400
```

#### Option 3: Testing Mode
```bash
# Test with small batch to verify Discord notifications
python src\production_scraper.py --max-items 10 --max-scrolls 5
```

## ⚙️ Configuration Options

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--max-items` | Max items to scan (0 = unlimited) | 0 | `--max-items 1000` |
| `--headless` | Run without browser window | False | `--headless` |
| `--max-scrolls` | Maximum scroll attempts | 50 | `--max-scrolls 400` |
| `--continuous` | Run continuously | False | `--continuous` |
| `--scan-interval` | Seconds between continuous scans | 10 | `--scan-interval 300` |

## 📈 Performance Expectations

### Continuous Monitoring Mode:
- **Notification Speed**: Instant alerts (< 5 seconds from discovery)
- **Scan Frequency**: Every 10 seconds by default
- **Memory Usage**: ~200-400MB in headless mode
- **Perfect for**: 24/7 VPS deployment

### Single Scan Mode (~19,000 items):
- **Duration**: 3-4 hours for full marketplace scan
- **Opportunities**: Typically 0-5 RED flags, 10-20 YELLOW/GREEN per scan
- **Perfect for**: One-time analysis or testing

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
- **Selenium WebDriver**: Automated Chrome browser interaction for NiftyGateway
- **Multiple Scroll Strategies**: Ensures maximum marketplace content discovery
- **Real-time Callbacks**: Instant notification system for time-sensitive opportunities

### Error Handling
- **Navigation Retries**: Failed page loads are retried automatically
- **Graceful Degradation**: Continues scanning even if individual items fail
- **Webhook Resilience**: Discord notification failures don't stop the scanning process
- **Comprehensive Logging**: Detailed progress and error reporting for debugging

### Anti-Detection Measures
- **Human-like Scrolling**: Multiple small scrolls to simulate user behavior
- **Random Delays**: Variable wait times between requests to appear natural
- **Standard User Agent**: Mimics regular Chrome browser interactions

## 📊 Discord Notification Examples

The system sends rich Discord embeds with detailed arbitrage information:

### 🔥 RED FLAG Alert Example:
```
🔥 EXCELLENT ARBITRAGE OPPORTUNITY 🔥
Collection: CryptoPunks #7804
💰 NiftyGateway Price: $15,000
🎯 OpenSea Top Offer: $16,500
📈 Potential Profit: $1,500 (10.0%)
🔗 Buy Now: [NiftyGateway Link]
💸 Sell Offer: [OpenSea Link]
⚡ IMMEDIATE ACTION REQUIRED
```

### 🟡 YELLOW FLAG Alert Example:
```
🟡 GOOD ARBITRAGE OPPORTUNITY
Collection: Board Ape #3829  
💰 NiftyGateway Price: $8,200
🎯 OpenSea Top Offer: $8,900
📈 Potential Profit: $700 (8.5%)
🔗 Buy Now: [NiftyGateway Link]
💸 Sell Offer: [OpenSea Link]
```

All notifications include direct purchase and sell links for immediate action.

## 🔧 Troubleshooting

### Common Issues

**Discord webhook not working:**
```bash
# Test your webhook URL manually:
curl -X POST -H "Content-Type: application/json" -d '{"content": "Test message"}' YOUR_WEBHOOK_URL
```

**No opportunities found:**
- Check internet connection and API availability
- Verify Discord webhook URL is valid
- Try reducing --max-items for testing

**Browser issues:**
- Update Chrome to latest version
- Use `--headless` for VPS deployment
- Check available system memory

**Rate limiting:**
- Built-in delays prevent most rate limiting
- If issues persist, increase scan intervals

**PowerShell Execution Policy Error**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**ChromeDriver Issues**:
- The scraper auto-downloads compatible ChromeDriver
- Ensure Chrome browser is updated to latest version

**Memory Issues (Large Scans)**:
- Close other applications
- Use `--headless` flag to reduce memory usage
- Consider running on VPS for 24/7 monitoring

### Performance Optimization

**For Maximum Speed**:
- Use `--headless` flag
- Close unnecessary applications
- Ensure stable internet connection
- Use continuous mode for real-time monitoring

**For Maximum Reliability**:
- Use VPS deployment for 24/7 operation
- Monitor Discord channel for notification health
- Set appropriate scan intervals for your use case

## 📝 Development

### Project Structure
The scanner is modular and extensible:
- **src/nifty_scraper.py**: Core scraping logic with real-time callbacks
- **src/production_scraper.py**: CLI interface for Discord alerts
- **src/discord_notifier.py**: Discord webhook client for rich notifications
- **src/opensea_offers_client.py**: Arbitrage analysis and opportunity detection
- **src/opensea_client.py**: Collection data enrichment

### Testing
```bash
# Test with small dataset and Discord notifications
python src\production_scraper.py --max-items 10 --max-scrolls 5

# Test continuous mode for short duration
python src\production_scraper.py --continuous --scan-interval 30 --max-items 50
```

### Adding New Features
- Extend arbitrage flagging logic in `opensea_offers_client.py`
- Customize Discord notification format in `discord_notifier.py`
- Add new command line options in `production_scraper.py`

## ⚠️ Important Notes

### Discord Notifications
- Set up your Discord webhook URL in the environment variable `DISCORD_WEBHOOK_URL`
- Test webhook connectivity before deploying for production
- Monitor notification frequency to avoid Discord rate limits

### Rate Limiting & API Usage
- Built-in delays prevent overwhelming NiftyGateway servers
- OpenSea API calls are rate-limited and cached when possible
- Use responsibly for legitimate arbitrage research purposes

### Real-Time Performance
- Notification speed depends on network latency and Discord response time
- Typical notification delay: < 5 seconds from opportunity discovery
- Consider VPS deployment near exchange servers for fastest alerts

### Data Accuracy
- Floor prices are extracted from the "List Price" column on NiftyGateway
- OpenSea offers reflect real bid data at time of scanning
- Price discrepancies may exist due to rapid market changes

### Legal Compliance
- This tool is for educational and arbitrage research purposes
- Ensure compliance with NiftyGateway and OpenSea terms of service
- Use scraped data responsibly and ethically
- Consider the legal implications of automated trading systems

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

**Happy arbitrage hunting! 🚀💰**

*Remember: This tool is designed for legitimate arbitrage research and real-time opportunity detection. Please use responsibly and in compliance with all applicable terms of service. Fast execution on arbitrage opportunities requires both speed and accuracy - this system delivers both.*
