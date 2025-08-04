"""
OpenSea API client for fetching collection information
"""

import requests
import time
import logging
from typing import Optional, Tuple
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

class OpenSeaAPIClient:
    """Client for interacting with OpenSea API v2"""
    
    def __init__(self, api_key: str = "64eb62dc71584e55b7d2d53ac082d921"):
        """
        Initialize OpenSea API client
        
        Args:
            api_key: OpenSea API key
        """
        self.api_key = api_key
        self.base_url = "https://api.opensea.io/api/v2/chain/ethereum/contract/"
        self.rate_limit = 4  # requests per second
        self.retry_delay = 3  # seconds
        self.max_retries = 3
        
        self.headers = {
            "accept": "application/json",
            "x-api-key": self.api_key
        }
        
        # Track last request time for rate limiting
        self.last_request_time = 0
        
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        time_since_last = time.time() - self.last_request_time
        min_interval = 1.0 / self.rate_limit  # 0.25 seconds for 4 req/sec
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
    
    def get_collection_info(self, contract_address: str, retries: int = 0) -> Tuple[Optional[str], Optional[str]]:
        """
        Get collection name and slug from OpenSea API
        
        Args:
            contract_address: Ethereum contract address
            retries: Current retry count
            
        Returns:
            Tuple of (collection_name, collection_slug) or (None, None) if failed
        """
        if not contract_address:
            logger.warning("Empty contract address provided")
            return None, None
            
        # Rate limiting
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}{contract_address}"
        
        try:
            logger.debug(f"Fetching collection info for contract: {contract_address}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                collection_name = data.get('name', 'Unknown')
                collection_slug = data.get('collection', 'unknown')
                
                logger.debug(f"✅ Retrieved: {collection_name} ({collection_slug})")
                return collection_name, collection_slug
            
            elif response.status_code == 429:  # Rate limited
                logger.warning(f"⚠️  Rate limited for contract {contract_address}. Waiting {self.retry_delay}s...")
                time.sleep(self.retry_delay)
                
                if retries < self.max_retries:
                    return self.get_collection_info(contract_address, retries + 1)
                else:
                    logger.error(f"❌ Max retries exceeded for contract {contract_address}")
                    return None, None
            
            elif response.status_code == 404:
                logger.warning(f"⚠️  Contract {contract_address} not found on OpenSea")
                return "Not Found", "not-found"
            
            else:
                logger.error(f"❌ API error {response.status_code} for contract {contract_address}")
                
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    return self.get_collection_info(contract_address, retries + 1)
                else:
                    logger.error(f"❌ Max retries exceeded for contract {contract_address}")
                    return None, None
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error for contract {contract_address}: {e}")
            
            if retries < self.max_retries:
                time.sleep(self.retry_delay)
                return self.get_collection_info(contract_address, retries + 1)
            else:
                logger.error(f"❌ Max retries exceeded for contract {contract_address}")
                return None, None
    
    def enrich_item_with_collection_info(self, item: dict) -> dict:
        """
        Enrich a scraped item with OpenSea collection information
        
        Args:
            item: Dictionary containing scraped item data
            
        Returns:
            Item dictionary enriched with collection_name and collection_slug
        """
        if not item or 'contract' not in item:
            logger.warning("Item missing contract field, cannot enrich")
            return item
        
        contract_address = item['contract']
        
        # Check if already enriched
        if 'collection_name' in item and 'collection_slug' in item:
            logger.debug(f"Item already has collection info for contract {contract_address}")
            return item
        
        # Get collection info
        collection_name, collection_slug = self.get_collection_info(contract_address)
        
        if collection_name and collection_slug:
            item['collection_name'] = collection_name
            item['collection_slug'] = collection_slug
            item['opensea_enriched_at'] = datetime.now().isoformat()
            
            logger.info(f"🔗 Enriched item with OpenSea data: {collection_name} ({collection_slug})")
        else:
            logger.warning(f"⚠️  Failed to enrich item with OpenSea data for contract {contract_address}")
            # Still mark when we attempted enrichment
            item['opensea_enriched_at'] = datetime.now().isoformat()
            item['opensea_enrichment_failed'] = True
        
        return item
