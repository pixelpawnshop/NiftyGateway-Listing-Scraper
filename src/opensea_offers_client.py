"""
OpenSea Offers API client for fetching top offers and calculating arbitrage opportunities
"""

import requests
import time
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

class OpenSeaOffersClient:
    """Client for interacting with OpenSea Offers API v2"""
    
    def __init__(self, api_key: str = "64eb62dc71584e55b7d2d53ac082d921"):
        """
        Initialize OpenSea Offers API client
        
        Args:
            api_key: OpenSea API key
        """
        self.api_key = api_key
        self.base_url = "https://api.opensea.io/api/v2/offers/collection/"
        self.rate_limit = 4  # requests per second
        self.retry_delay = 3  # seconds
        self.max_retries = 3
        self.wei_to_eth = 1e18
        
        self.headers = {
            "accept": "application/json",
            "x-api-key": self.api_key
        }
        
        # ETH price caching
        self.eth_price_usd = None
        self.eth_price_last_updated = None
        self.eth_price_cache_minutes = 1  # Update ETH price every minute
        
        # Track last request time for rate limiting
        self.last_request_time = 0
        
        # Initialize ETH price
        self.update_eth_price()
        
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        time_since_last = time.time() - self.last_request_time
        min_interval = 1.0 / self.rate_limit  # 0.25 seconds for 4 req/sec
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
    
    def update_eth_price(self) -> bool:
        """
        Update ETH price from CoinGecko API
        
        Returns:
            True if price was updated successfully, False otherwise
        """
        try:
            # Check if we need to update (every minute)
            if (self.eth_price_last_updated and 
                datetime.now() - self.eth_price_last_updated < timedelta(minutes=self.eth_price_cache_minutes)):
                return True  # Price is still fresh
            
            # Fetch current ETH price from CoinGecko (free API, no key required)
            url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                new_price = data['ethereum']['usd']
                
                if self.eth_price_usd != new_price:
                    logger.info(f"💰 ETH price updated: ${new_price}")
                
                self.eth_price_usd = new_price
                self.eth_price_last_updated = datetime.now()
                return True
            else:
                logger.warning(f"Failed to fetch ETH price: HTTP {response.status_code}")
                # Use fallback price if we don't have one yet
                if self.eth_price_usd is None:
                    self.eth_price_usd = 3550  # Fallback price
                    logger.info(f"Using fallback ETH price: ${self.eth_price_usd}")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching ETH price: {e}")
            # Use fallback price if we don't have one yet
            if self.eth_price_usd is None:
                self.eth_price_usd = 3550  # Fallback price
                logger.info(f"Using fallback ETH price: ${self.eth_price_usd}")
            return False
    
    def wei_to_usd(self, wei_amount: str) -> Tuple[float, float]:
        """
        Convert Wei to ETH and USD
        
        Args:
            wei_amount: Amount in Wei as string
            
        Returns:
            Tuple of (eth_amount, usd_amount)
        """
        try:
            # Ensure we have current ETH price
            self.update_eth_price()
            
            eth_amount = int(wei_amount) / self.wei_to_eth
            usd_amount = eth_amount * self.eth_price_usd
            return eth_amount, usd_amount
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting Wei to USD: {e}")
            return 0.0, 0.0
    
    def get_arbitrage_flag(self, opensea_offer_usd: float, nifty_price_usd: float) -> Tuple[str, str, float]:
        """
        Determine arbitrage flag based on OpenSea offer vs Nifty Gateway price
        
        Args:
            opensea_offer_usd: OpenSea top offer in USD
            nifty_price_usd: NiftyGateway listing price in USD
            
        Returns:
            Tuple of (flag, description, profit_percentage)
        """
        # Calculate how much higher the OpenSea offer is compared to Nifty price
        # Positive percentage means OpenSea offer is higher (good for arbitrage)
        # Formula: ((opensea_offer - nifty_price) / nifty_price) * 100
        profit_percentage = ((opensea_offer_usd - nifty_price_usd) / nifty_price_usd) * 100
        
        if opensea_offer_usd >= nifty_price_usd:
            return "🔥 RED", "OpenSea offer >= Nifty price - EXCELLENT arbitrage (instant profit)", profit_percentage
        elif profit_percentage >= -10:  # OpenSea offer is within 10% of Nifty price
            return "🟡 YELLOW", "OpenSea offer within 10% of Nifty price - GOOD arbitrage potential", profit_percentage
        elif profit_percentage >= -20:  # OpenSea offer is within 20% of Nifty price
            return "🟢 GREEN", "OpenSea offer within 20% of Nifty price - FAIR arbitrage potential", profit_percentage
        else:
            return "⚪ WHITE", "OpenSea offer more than 20% below Nifty price - LIMITED arbitrage potential", profit_percentage
    
    def get_best_offer(self, collection_slug: str, token_id: str, retries: int = 0) -> Optional[Dict]:
        """
        Get best offer from OpenSea API
        
        Args:
            collection_slug: OpenSea collection slug
            token_id: Token ID
            retries: Current retry count
            
        Returns:
            Dictionary with offer data or None if no offer found
        """
        if not collection_slug or not token_id or collection_slug in ['unknown', 'not-found']:
            return None
            
        # Rate limiting
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}{collection_slug}/nfts/{token_id}/best"
        
        try:
            logger.debug(f"Fetching best offer for {collection_slug}/{token_id}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if there's an offer
                if not data or 'protocol_data' not in data:
                    logger.debug(f"No offers found for {collection_slug}/{token_id}")
                    return None
                
                # Extract offer amount from the protocol data
                try:
                    offer_amount_wei = data['protocol_data']['parameters']['offer'][0]['startAmount']
                    
                    # Check for quantity in consideration array (itemType 4 indicates ERC-1155 with quantity)
                    quantity = 1  # Default quantity
                    considerations = data['protocol_data']['parameters'].get('consideration', [])
                    
                    for consideration in considerations:
                        # itemType 4 = ERC-1155 (can have quantities > 1)
                        # itemType 2 = ERC-721 (always quantity = 1)
                        if consideration.get('itemType') == 4:
                            try:
                                quantity = int(consideration.get('startAmount', '1'))
                                logger.debug(f"Found quantity {quantity} for {collection_slug}/{token_id}")
                                break
                            except (ValueError, TypeError):
                                continue
                    
                    # Calculate per-item offer amount
                    per_item_offer_wei = str(int(int(offer_amount_wei) / quantity))
                    
                    # Convert to ETH and USD (using per-item amount)
                    offer_eth, offer_usd = self.wei_to_usd(per_item_offer_wei)
                    
                    offer_data = {
                        'offer_amount_wei': per_item_offer_wei,  # Per-item amount
                        'offer_amount_eth': round(offer_eth, 6),
                        'offer_amount_usd': round(offer_usd, 2),
                        'total_offer_wei': offer_amount_wei,  # Total offer amount
                        'quantity': quantity,  # Number of items in the offer
                        'order_hash': data.get('order_hash'),
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    if quantity > 1:
                        logger.info(f"✅ Multi-quantity offer: {quantity}x {offer_eth:.4f} ETH each (${offer_usd:.2f} per item) for {collection_slug}/{token_id}")
                    else:
                        logger.debug(f"✅ Single offer: {offer_eth:.4f} ETH (${offer_usd:.2f}) for {collection_slug}/{token_id}")
                    
                    return offer_data
                    
                except (KeyError, IndexError) as e:
                    logger.warning(f"Error extracting offer amount for {collection_slug}/{token_id}: {e}")
                    return None
            
            elif response.status_code == 404:
                logger.debug(f"No offers found for {collection_slug}/{token_id}")
                return None
            
            elif response.status_code == 429:  # Rate limited
                logger.warning(f"⚠️  Rate limited for {collection_slug}/{token_id}. Waiting {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                
                if retries < self.max_retries:
                    return self.get_best_offer(collection_slug, token_id, retries + 1)
                else:
                    logger.error(f"❌ Max retries exceeded for {collection_slug}/{token_id}")
                    return None
            
            else:
                logger.error(f"❌ API error {response.status_code} for {collection_slug}/{token_id}")
                
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    return self.get_best_offer(collection_slug, token_id, retries + 1)
                else:
                    logger.error(f"❌ Max retries exceeded for {collection_slug}/{token_id}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error for {collection_slug}/{token_id}: {e}")
            
            if retries < self.max_retries:
                time.sleep(self.retry_delay)
                return self.get_best_offer(collection_slug, token_id, retries + 1)
            else:
                logger.error(f"❌ Max retries exceeded for {collection_slug}/{token_id}")
                return None
    
    def enrich_item_with_arbitrage_data(self, item: dict) -> dict:
        """
        Enrich a scraped item with OpenSea arbitrage opportunity data
        
        Args:
            item: Dictionary containing scraped item data with collection info
            
        Returns:
            Item dictionary enriched with arbitrage data
        """
        if not item or not all(k in item for k in ['collection_slug', 'actual_token_id', 'floor_price']):
            logger.warning("Item missing required fields for arbitrage analysis")
            return item
        
        collection_slug = item['collection_slug']
        token_id = item['actual_token_id']
        nifty_price = item['floor_price']
        contract_address = item.get('contract')
        
        # Check if already enriched
        if 'opensea_offer_data' in item:
            logger.debug(f"Item already has arbitrage data for {collection_slug}/{token_id}")
            return item
        
        # Build OpenSea item URL
        opensea_item_url = None
        if contract_address and token_id:
            opensea_item_url = f"https://opensea.io/assets/ethereum/{contract_address}/{token_id}"
        
        # Get best offer data
        offer_data = self.get_best_offer(collection_slug, token_id)
        
        if offer_data:
            # Calculate arbitrage flag and profit potential
            flag, description, profit_percentage = self.get_arbitrage_flag(
                offer_data['offer_amount_usd'], 
                nifty_price
            )
            
            # Add arbitrage analysis to item
            item['opensea_offer_data'] = offer_data
            item['arbitrage_flag'] = flag
            item['arbitrage_description'] = description
            item['profit_percentage'] = round(profit_percentage, 2)
            item['potential_profit_usd'] = round(offer_data['offer_amount_usd'] - nifty_price, 2)
            item['arbitrage_analyzed_at'] = datetime.now().isoformat()
            
            # Add OpenSea URLs
            if opensea_item_url:
                item['opensea_item_url'] = opensea_item_url
            if collection_slug and collection_slug not in ['unknown', 'not-found']:
                item['opensea_collection_url'] = f"https://opensea.io/collection/{collection_slug}"
            
            # Log significant arbitrage opportunities
            if profit_percentage >= -10:  # Only log good opportunities
                logger.info(f"💎 ARBITRAGE: {flag} - {collection_slug} #{token_id}")
                logger.info(f"   OpenSea: ${offer_data['offer_amount_usd']:.2f} | Nifty: ${nifty_price:.2f} | Profit: {profit_percentage:+.1f}%")
                if opensea_item_url:
                    logger.info(f"   OpenSea URL: {opensea_item_url}")
            else:
                logger.debug(f"Arbitrage checked: {collection_slug} #{token_id} - {profit_percentage:+.1f}%")
        else:
            # No offer found
            item['opensea_offer_data'] = None
            item['arbitrage_flag'] = "⚫ NO_OFFER"
            item['arbitrage_description'] = "No offers found on OpenSea"
            item['arbitrage_analyzed_at'] = datetime.now().isoformat()
            
            # Still add OpenSea URLs even if no offers
            if opensea_item_url:
                item['opensea_item_url'] = opensea_item_url
            if collection_slug and collection_slug not in ['unknown', 'not-found']:
                item['opensea_collection_url'] = f"https://opensea.io/collection/{collection_slug}"
            
            logger.debug(f"No offers found for {collection_slug}/{token_id}")
        
        return item
