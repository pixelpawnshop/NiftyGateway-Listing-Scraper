"""
NiftyGateway Scraper Configuration
"""

# Scraper settings
DEFAULT_MAX_ITEMS = 1000  # Increased for production
DEFAULT_MAX_SCROLLS = 50  # Increased for production
DEFAULT_SCROLL_PAUSE_TIME = 1.0  # Reduced for speed
DEFAULT_WAIT_TIMEOUT = 10

# Browser settings
HEADLESS_MODE = True  # Default to headless for production
WINDOW_SIZE = "1920,1080"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# URL patterns
NIFTY_GATEWAY_BASE_URL = "https://www.niftygateway.com"
BASE_URL = "https://www.niftygateway.com/explore/nfts/?sort=-likes&chain%5B0%5D=ethereum&tags=Generative%20Art%2CPainting%2CCollage%2CDigital%20Painting%20and%20Drawing"
ART_CATEGORY_URL = "https://www.niftygateway.com/explore/nfts/?sort=-likes&chain%5B0%5D=ethereum&tags=Generative%20Art%2CPainting%2CCollage%2CDigital%20Painting%20and%20Drawing"

# CSS Selectors for different elements
ITEM_SELECTORS = [
    "[data-testid='nft-card']",
    ".marketplace-item",
    "[href*='/marketplace/collectible/']",
    "[href*='/marketplace/collection/']",
    "a[href*='/marketplace/']"
]

TITLE_SELECTORS = [
    "h3", "h2", ".title", "[data-testid='nft-title']", 
    ".item-title", ".collection-name"
]

CREATOR_SELECTORS = [
    ".creator", "[data-testid='creator']", ".artist", 
    ".author", "[class*='creator']"
]

PRICE_SELECTORS = [
    "[class*='price']", "[data-testid='price']", 
    ".floor-price", "[class*='floor']"
]

COUNT_SELECTORS = [
    "[class*='items']", "[class*='count']", 
    "[data-testid='item-count']"
]

# File output settings
CSV_FILENAME_TEMPLATE = "nifty_gateway_items_{timestamp}.csv"
JSON_FILENAME_TEMPLATE = "nifty_gateway_items_{timestamp}.json"

# Error handling
MAX_RETRIES = 3
RETRY_DELAY = 1.0
