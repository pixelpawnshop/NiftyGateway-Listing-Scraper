import time
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


class NiftyGatewayScraper:
    def __init__(self, headless: bool = False):
        """
        Initialize the NiftyGateway scraper
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.driver = None
        self.headless = headless
        self.scraped_items = []
        
    def setup_driver(self):
        """Set up Chrome WebDriver with options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        # Let webdriver-manager auto-detect and download compatible driver
        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def extract_contract_and_id(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract contract address and token ID from NiftyGateway URL
        
        Args:
            url: NiftyGateway marketplace URL
            
        Returns:
            Dictionary containing contract and id (if available)
        """
        contract_pattern = r'/marketplace/(?:collectible|collection)/([a-fA-F0-9x]+)(?:/(\d+))?'
        match = re.search(contract_pattern, url)
        
        if match:
            contract = match.group(1)
            token_id = match.group(2) if match.group(2) else None
            return {
                'contract': contract,
                'token_id': token_id,
                'url_type': 'collection' if token_id else 'collectible'
            }
        
        return {'contract': None, 'token_id': None, 'url_type': None}
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from price text
        
        Args:
            price_text: Text containing price information
            
        Returns:
            Float price or None if not found
        """
        price_pattern = r'\$([0-9,]+\.?[0-9]*)'
        match = re.search(price_pattern, price_text)
        
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    def wait_for_items_to_load(self, timeout: int = 10) -> bool:
        """
        Wait for NFT items to load on the page
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if items loaded, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='nft-card'], .marketplace-item, [href*='/marketplace/']"))
            )
            return True
        except TimeoutException:
            print("Timeout waiting for items to load")
            return False
    
    def scroll_to_load_more(self, scroll_pause_time: float = 2.0) -> bool:
        """
        Scroll down to trigger loading of more items with multiple strategies
        
        Args:
            scroll_pause_time: Time to wait after scrolling
            
        Returns:
            True if more content was loaded, False otherwise
        """
        try:
            # Count current items before scrolling
            initial_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
            items_before = len(initial_items)
            print(f"Items before scroll: {items_before}")
            
            # Strategy 1: Multiple small scrolls to simulate user behavior
            for scroll_step in range(5):
                current_position = self.driver.execute_script("return window.pageYOffset")
                scroll_amount = 800  # Smaller scroll amounts
                self.driver.execute_script(f"window.scrollTo(0, {current_position + scroll_amount});")
                time.sleep(0.5)  # Short pause between scrolls
                
                # Check for new items after each small scroll
                current_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
                if len(current_items) > items_before:
                    print(f"Found {len(current_items) - items_before} new items after small scroll {scroll_step + 1}")
                    return True
            
            # Strategy 2: Scroll to specific percentages of page
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            for percentage in [0.25, 0.5, 0.75, 1.0]:
                target_position = int(page_height * percentage)
                self.driver.execute_script(f"window.scrollTo(0, {target_position});")
                time.sleep(2)
                
                current_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
                if len(current_items) > items_before:
                    print(f"Found {len(current_items) - items_before} new items after scrolling to {percentage*100}%")
                    return True
            
            # Strategy 3: Use keyboard navigation
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                for i in range(10):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.3)
                    
                    current_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
                    if len(current_items) > items_before:
                        print(f"Found {len(current_items) - items_before} new items after PAGE_DOWN {i + 1}")
                        return True
            except Exception as e:
                print(f"Keyboard navigation failed: {e}")
            
            # Strategy 4: Try to find and click a "Load More" button
            try:
                load_more_selectors = [
                    "button[data-testid='load-more']",
                    "button:contains('Load More')",
                    "button:contains('Show More')",
                    "[data-testid='load-more-button']",
                    ".load-more",
                    "button[class*='load']",
                    "button[class*='more']"
                ]
                
                for selector in load_more_selectors:
                    try:
                        if ":contains(" in selector:
                            # Use XPath for text-based selection
                            xpath_selector = f"//button[contains(text(), 'Load More') or contains(text(), 'Show More')]"
                            load_button = self.driver.find_element(By.XPATH, xpath_selector)
                        else:
                            load_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if load_button.is_displayed() and load_button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", load_button)
                            time.sleep(3)
                            
                            current_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
                            if len(current_items) > items_before:
                                print(f"Found {len(current_items) - items_before} new items after clicking load more button")
                                return True
                    except:
                        continue
            except Exception as e:
                print(f"Load more button search failed: {e}")
            
            # Strategy 5: Aggressive scrolling with longer waits
            print("Trying aggressive scrolling...")
            for attempt in range(3):
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)  # Longer wait
                
                # Check for new content
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                current_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
                
                if len(current_items) > items_before:
                    print(f"Found {len(current_items) - items_before} new items after aggressive scroll {attempt + 1}")
                    return True
                
                # Try scrolling past the bottom
                self.driver.execute_script(f"window.scrollTo(0, {new_height + 1000});")
                time.sleep(3)
                
                final_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
                if len(final_items) > items_before:
                    print(f"Found {len(final_items) - items_before} new items after over-scroll")
                    return True
            
            # Final check
            final_items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
            items_after = len(final_items)
            
            if items_after > items_before:
                print(f"Scroll successful: {items_after - items_before} new items found")
                return True
            else:
                print(f"No new content found after all strategies. Items: {items_before} -> {items_after}")
                return False
                
        except Exception as e:
            print(f"Error during scrolling: {e}")
            return False
    
    def wait_for_items_to_load(self, timeout: int = 10) -> bool:
        """
        Wait for items to load on the page
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if items loaded, False if timeout
        """
        try:
            print("Waiting for items to load...")
            
            # Wait for at least some items to appear
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for marketplace collection links to appear
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[href*='/marketplace/collection/']")))
            
            # Give extra time for all items to load
            time.sleep(2)
            
            items = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
            print(f"Found {len(items)} items after waiting")
            
            return len(items) > 0
            
        except Exception as e:
            print(f"Error waiting for items: {e}")
            return False

    def get_all_collection_urls(self) -> List[str]:
        """
        Get all collection URLs from the current page
        
        Returns:
            List of unique collection URLs
        """
        try:
            # Wait for items to load first
            self.wait_for_items_to_load()
            
            # Get all collection links
            collection_links = self.driver.find_elements(By.CSS_SELECTOR, "[href*='/marketplace/collection/']")
            
            urls = []
            for link in collection_links:
                try:
                    href = link.get_attribute('href')
                    if href and '/marketplace/collection/' in href:
                        # Normalize URL (remove query params, fragments)
                        base_url = href.split('?')[0].split('#')[0]
                        if base_url not in urls:
                            urls.append(base_url)
                except Exception as e:
                    print(f"Error getting href from link: {e}")
                    continue
            
            print(f"Found {len(urls)} unique collection URLs")
            return urls
            
        except Exception as e:
            print(f"Error getting collection URLs: {e}")
            return []
    
    def extract_item_data_from_page(self, item_url: str) -> Optional[Dict]:
        """
        Extract item data from the current page (when already navigated to collection page)
        
        Args:
            item_url: The collection URL we're currently on
            
        Returns:
            Dictionary containing item data or None if extraction failed
        """
        try:
            # Get contract info from URL
            contract_info = self.extract_contract_and_id(item_url)
            
            # Get page text for basic extractions
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Fast text-based extraction
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            
            # Extract title - look for the main heading
            title = "Unknown"
            for line in lines[:10]:  # Check first 10 lines
                if line and not line.startswith('$') and len(line) > 3:
                    title = line
                    break
            
            # Extract creator
            creator = "Unknown"
            for i, line in enumerate(lines):
                if "created by" in line.lower() or "creator" in line.lower():
                    if i + 1 < len(lines):
                        creator = lines[i + 1]
                        break
            
            # Extract item count
            item_count = None
            for line in lines:
                count_match = re.search(r'(\d+)\s*[Ii]tems', line)
                if count_match:
                    try:
                        item_count = int(count_match.group(1))
                        break
                    except ValueError:
                        pass
            
            # Get floor price and token ID directly from the marketplace table
            table_data = self.get_cheapest_token_id_and_price_from_current_page()
            
            floor_price = None
            floor_price_text = ""
            actual_token_id = None
            
            if table_data:
                actual_token_id = table_data.get('token_id')
                list_price_str = table_data.get('list_price')
                
                if list_price_str:
                    try:
                        floor_price = float(list_price_str)
                        floor_price_text = f"${list_price_str} (Table List Price)"
                    except ValueError:
                        pass
            
            return {
                'floor_price': floor_price,
                'floor_price_text': floor_price_text,
                'contract': contract_info['contract'],
                'actual_token_id': actual_token_id,
                'marketplace_url': item_url,
                'actual_marketplace_url': None,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return None

    def get_cheapest_token_id_and_price_from_current_page(self) -> Optional[Dict[str, str]]:
        """
        Find the token ID and list price of the cheapest item from the current collection page
        
        Returns:
            Dictionary with token_id and list_price or None if not found
        """
        try:
            # Wait for the marketplace items table to load
            time.sleep(1)  # Reduced from 3 to 1 second
            
            # Look for the marketplace items table - try different approaches
            table_selectors = [
                "table tbody tr",
                ".MuiTableBody-root tr",
                "[class*='MuiTableBody'] tr",
                "tbody tr"
            ]
            
            cheapest_item = None
            for selector in table_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        # The first item should be the cheapest (sorted by price)
                        cheapest_item = items[0]
                        break
                except NoSuchElementException:
                    continue
            
            if not cheapest_item:
                # Try finding links directly
                link_selectors = [
                    "a[href*='/marketplace/item/']",
                    "[href*='/marketplace/item/']"
                ]
                
                for selector in link_selectors:
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if links:
                            # First link should be cheapest
                            item_url = links[0].get_attribute('href')
                            if item_url and '/marketplace/item/' in item_url:
                                token_match = re.search(r'/marketplace/item/[^/]+/(\d+)/', item_url)
                                if token_match:
                                    token_id = token_match.group(1)
                                    return {'token_id': token_id, 'list_price': None}
                            break
                    except NoSuchElementException:
                        continue
                        
                return None
            
            # Found a table row, extract both token ID and list price
            token_id = None
            list_price = None
            
            # Get token ID from link
            try:
                # Look for link with marketplace/item pattern inside the row
                link = cheapest_item.find_element(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")
                item_url = link.get_attribute('href')
                
                if item_url and '/marketplace/item/' in item_url:
                    # Extract token ID from URL like: /marketplace/item/0x123.../8666/
                    token_match = re.search(r'/marketplace/item/[^/]+/(\d+)/', item_url)
                    if token_match:
                        token_id = token_match.group(1)
                
            except NoSuchElementException:
                pass
            
            # Alternative: look for the token ID in the text content (like "#8666 / 15045")
            if not token_id:
                try:
                    item_text = cheapest_item.text
                    
                    # Look for patterns like "#8666 / 15045" or "#8666/15045"
                    token_patterns = [
                        r'#(\d+)\s*/\s*\d+',  # "#8666 / 15045"
                        r'#(\d+)/\d+',        # "#8666/15045"
                        r'#(\d+)',            # "#8666"
                    ]
                    
                    for pattern in token_patterns:
                        match = re.search(pattern, item_text)
                        if match:
                            token_id = match.group(1)
                            break
                            
                except Exception as e:
                    pass
            
            # Extract list price from the table row - specifically from List Price column
            try:
                # Get all table cells in this row
                cells = cheapest_item.find_elements(By.CSS_SELECTOR, "td, .MuiTableCell-root, [class*='MuiTableCell']")
                
                # Look for the List Price column specifically
                list_price = None
                
                # Method 1: Try to find List Price column by looking at header structure
                try:
                    # Get the table header to understand column structure
                    table = cheapest_item.find_element(By.XPATH, "./ancestor::table")
                    headers = table.find_elements(By.CSS_SELECTOR, "th, .MuiTableHead-root th, [class*='MuiTableHead'] th")
                    
                    list_price_column_index = None
                    for i, header in enumerate(headers):
                        if "list price" in header.text.lower():
                            list_price_column_index = i
                            break
                    
                    if list_price_column_index is not None and list_price_column_index < len(cells):
                        list_price_cell = cells[list_price_column_index]
                        price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', list_price_cell.text)
                        if price_match:
                            list_price = price_match.group(1).replace(',', '')
                            
                except Exception:
                    pass
                
                # Method 2: If we couldn't find by header, look for the rightmost price (usually List Price)
                if not list_price:
                    prices_found = []
                    for cell in cells:
                        cell_text = cell.text.strip()
                        price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', cell_text)
                        if price_match:
                            prices_found.append((price_match.group(1).replace(',', ''), cell_text))
                    
                    # Take the last price found (rightmost column, which is usually List Price)
                    if prices_found:
                        list_price = prices_found[-1][0]
                
                # Method 3: Fallback - look for specific patterns that indicate list price
                if not list_price:
                    row_text = cheapest_item.text
                    # Look for price that's NOT associated with "Last Sale" or sale dates
                    lines = row_text.split('\n')
                    for line in lines:
                        if ('$' in line and 
                            'last sale' not in line.lower() and 
                            'sale time' not in line.lower() and
                            'dec ' not in line.lower() and  # Avoid sale dates
                            'jan ' not in line.lower() and
                            'feb ' not in line.lower() and
                            'mar ' not in line.lower() and
                            'apr ' not in line.lower() and
                            'may ' not in line.lower() and
                            'jun ' not in line.lower() and
                            'jul ' not in line.lower() and
                            'aug ' not in line.lower() and
                            'sep ' not in line.lower() and
                            'oct ' not in line.lower() and
                            'nov ' not in line.lower()):
                            
                            price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', line)
                            if price_match:
                                list_price = price_match.group(1).replace(',', '')
                                break
                    
            except Exception as e:
                pass
            
            if token_id:
                return {'token_id': token_id, 'list_price': list_price}
            
            return None
            
        except Exception as e:
            return None

    def get_cheapest_token_id(self, collection_url: str) -> Optional[str]:
        """
        Navigate to a collection page and find the token ID of the cheapest item
        
        Args:
            collection_url: URL of the collection page
            
        Returns:
            Token ID string of the cheapest item or None if not found
        """
        try:
            print(f"Loading collection page: {collection_url}")
            self.driver.get(collection_url)
            
            # Wait for the marketplace items table to load
            time.sleep(3)
            
            # Look for the marketplace items table
            table_selectors = [
                "table tbody tr",
                "[data-testid='marketplace-item']",
                ".marketplace-table tr",
                "tr[href*='/marketplace/item/']",
                "a[href*='/marketplace/item/']"
            ]
            
            cheapest_item = None
            for selector in table_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        print(f"Found {len(items)} items in table with selector: {selector}")
                        # The first item should be the cheapest (sorted by price)
                        cheapest_item = items[0]
                        break
                except NoSuchElementException:
                    continue
            
            if not cheapest_item:
                print("No items found in marketplace table")
                return None
            
            # Try to get the item URL directly
            item_url = cheapest_item.get_attribute('href')
            if not item_url:
                # If the row doesn't have href, look for a link inside it
                try:
                    link = cheapest_item.find_element(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")
                    item_url = link.get_attribute('href')
                except NoSuchElementException:
                    pass
            
            if item_url and '/marketplace/item/' in item_url:
                # Extract token ID from URL like: /marketplace/item/0x123.../28/
                import re
                token_match = re.search(r'/marketplace/item/[^/]+/(\d+)/', item_url)
                if token_match:
                    token_id = token_match.group(1)
                    print(f"Found cheapest token ID: {token_id}")
                    return token_id
            
            # Alternative approach: look for token ID in the text content
            try:
                item_text = cheapest_item.text
                print(f"Item text: {item_text}")
                
                # Look for patterns like "#28" or "28 /" in the text
                token_patterns = [
                    r'#(\d+)',
                    r'^(\d+)\s*/',
                    r'(\d+)\s*/\s*\d+'
                ]
                
                for pattern in token_patterns:
                    match = re.search(pattern, item_text)
                    if match:
                        token_id = match.group(1)
                        print(f"Found token ID from text: {token_id}")
                        return token_id
                        
            except Exception as e:
                print(f"Error extracting token ID from text: {e}")
            
            print("Could not extract token ID from cheapest item")
            return None
            
        except Exception as e:
            print(f"Error getting cheapest token ID: {str(e)}")
            return None

    def extract_item_data(self, item_element) -> Optional[Dict]:
        """
        Fast extraction using text parsing instead of complex DOM searching
        
        Args:
            item_element: Selenium WebElement representing an NFT item
            
        Returns:
            Dictionary containing item data or None if extraction failed
        """
        try:
            # Get the URL (item_element should be a link)
            item_url = item_element.get_attribute('href')
            if not item_url or '/marketplace/' not in item_url:
                return None
            
            # Get contract info
            contract_info = self.extract_contract_and_id(item_url)
            
            # Find parent container for text extraction
            extraction_element = item_element
            try:
                extraction_element = item_element.find_element(By.XPATH, "..")
            except:
                pass
            
            # Get all text from the container
            all_text = extraction_element.text
            if not all_text:
                return None
            
            # Fast text-based extraction
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # Extract title (usually first line)
            title = lines[0] if lines else "Unknown"
            
            # Extract creator (look for "Creator:" pattern)
            creator = "Unknown"
            for i, line in enumerate(lines):
                if line.lower() == "creator:" and i + 1 < len(lines):
                    creator = lines[i + 1]
                    break
                elif "creator:" in line.lower() and line.strip() != "Creator:":
                    creator = line.replace("Creator:", "").strip()
                    break
            
            # Extract floor price using regex
            floor_price = None
            floor_price_text = ""
            import re
            
            # Look for price pattern in text
            price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', all_text)
            if price_match and "floor" in all_text.lower():
                price_str = price_match.group(1).replace(',', '')
                try:
                    floor_price = float(price_str)
                    floor_price_text = f"${price_str} Floor Price"
                except ValueError:
                    pass
            
            # Extract item count
            item_count = None
            count_match = re.search(r'(\d+)\s*[Ii]tems', all_text)
            if count_match:
                try:
                    item_count = int(count_match.group(1))
                except ValueError:
                    pass
            
            return {
                'title': title,
                'creator': creator,
                'floor_price': floor_price,
                'floor_price_text': floor_price_text,
                'item_count': item_count,
                'contract': contract_info['contract'],
                'token_id': contract_info['token_id'],  # This is from the collection URL structure
                'actual_token_id': None,  # This will be filled later from the cheapest item
                'url_type': contract_info['url_type'],
                'marketplace_url': item_url,  # Original collection URL
                'actual_marketplace_url': None,  # This will be filled later with the specific item URL
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting item data: {str(e)}")
            return None
    
    def scrape_items(self, url: str, max_items: int = 100, max_scrolls: int = 20) -> List[Dict]:
        """
        Scrape NFT items from NiftyGateway using two-phase approach:
        Phase 1: Collect ALL collection URLs by scrolling
        Phase 2: Process each URL to extract floor price data
        
        Args:
            url: NiftyGateway URL to scrape
            max_items: Maximum number of items to scrape
            max_scrolls: Maximum number of scroll attempts
            
        Returns:
            List of dictionaries containing item data
        """
        if not self.driver:
            self.setup_driver()
        
        print(f"Loading page: {url}")
        self.driver.get(url)
        
        # Wait for initial items to load
        if not self.wait_for_items_to_load():
            print("Failed to load initial items")
            return []

        print("\n🔍 Phase 1: Collecting ALL collection URLs with aggressive scrolling...")
        all_collection_urls = self.collect_all_urls_with_scrolling(max_scrolls)
        
        if not all_collection_urls:
            print("❌ No collection URLs found")
            return []
        
        print(f"📊 Total collection URLs found: {len(all_collection_urls)}")
        
        # Limit URLs if max_items specified
        if max_items > 0 and max_items < len(all_collection_urls):
            all_collection_urls = all_collection_urls[:max_items]
            print(f"🎯 Limited to first {max_items} URLs")
        
        print(f"\n⚙️ Phase 2: Processing {len(all_collection_urls)} collection URLs...")
        
        # Process each URL to get floor price data
        scraped_count = 0
        for i, collection_url in enumerate(all_collection_urls, 1):
            try:
                print(f"\n🔄 Processing {i}/{len(all_collection_urls)}: {collection_url}")
                
                # Navigate to collection page
                self.driver.get(collection_url)
                time.sleep(1)  # Brief wait for page load
                
                # Extract item data
                item_data = self.extract_item_data_from_page(collection_url)
                
                if not item_data:
                    print(f"❌ Failed to extract data")
                    continue
                
                if item_data['floor_price'] is None:
                    print(f"⚠️  No floor price found")
                    continue
                    
                # Check if this is a collection item (we need contract_info for validation)
                contract_info = self.extract_contract_and_id(collection_url)
                if contract_info['url_type'] != 'collection':
                    print(f"⚠️  Not a collection item")
                    continue
                    
                actual_token_id = item_data['actual_token_id']
                if not actual_token_id:
                    print(f"⚠️  No token ID found")
                    continue
                
                # Build the actual marketplace URL for the cheapest item
                if actual_token_id:
                    item_data['actual_marketplace_url'] = f"https://www.niftygateway.com/marketplace/item/{item_data['contract']}/{actual_token_id}/"
                    
                    self.scraped_items.append(item_data)
                    scraped_count += 1
                    print(f"✅ Scraped item {scraped_count}: Floor: ${item_data['floor_price']} - Token: #{actual_token_id}")
                
                # Brief pause between requests
                time.sleep(0.5)
                
                # Progress update every 10 items
                if i % 10 == 0:
                    print(f"\n📈 Progress: {i}/{len(all_collection_urls)} URLs processed, {scraped_count} items scraped")
                
            except Exception as e:
                print(f"❌ Error processing {collection_url}: {e}")
                continue
        
        print(f"\n🎉 Scraping completed! Total items with floor prices: {len(self.scraped_items)}")
        return self.scraped_items

    def collect_all_urls_with_scrolling(self, max_scrolls: int = 20) -> List[str]:
        """
        Aggressively collect ALL collection URLs by scrolling until no more content loads
        
        Args:
            max_scrolls: Maximum scroll attempts
            
        Returns:
            List of all unique collection URLs found
        """
        all_urls = set()
        scroll_attempts = 0
        consecutive_no_new = 0
        
        try:
            print("🔄 Starting aggressive URL collection...")
            
            # Initial collection
            initial_urls = self.get_all_collection_urls_on_page()
            all_urls.update(initial_urls)
            print(f"📦 Initial load: {len(initial_urls)} URLs")
            
            while scroll_attempts < max_scrolls and consecutive_no_new < 3:
                print(f"\n📜 Scroll attempt {scroll_attempts + 1}/{max_scrolls}")
                
                urls_before = len(all_urls)
                
                # Try multiple scrolling strategies in sequence
                scroll_success = False
                
                # Strategy 1: Scroll to bottom and wait
                print("  📍 Strategy 1: Scroll to bottom")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                current_urls = self.get_all_collection_urls_on_page()
                new_urls_count = len(set(current_urls) - all_urls)
                all_urls.update(current_urls)
                
                if new_urls_count > 0:
                    print(f"    ✅ Found {new_urls_count} new URLs")
                    scroll_success = True
                else:
                    # Strategy 2: Multiple small scrolls
                    print("  📍 Strategy 2: Progressive scrolling")
                    current_position = self.driver.execute_script("return window.pageYOffset")
                    
                    for step in range(5):
                        scroll_amount = 1000 + (step * 500)
                        new_position = current_position + scroll_amount
                        self.driver.execute_script(f"window.scrollTo(0, {new_position});")
                        time.sleep(1)
                        
                        step_urls = self.get_all_collection_urls_on_page()
                        step_new_count = len(set(step_urls) - all_urls)
                        all_urls.update(step_urls)
                        
                        if step_new_count > 0:
                            print(f"    ✅ Found {step_new_count} new URLs at position {new_position}")
                            scroll_success = True
                            break
                
                # Strategy 3: Page down keys if other methods fail
                if not scroll_success:
                    print("  📍 Strategy 3: Keyboard navigation")
                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        for key_attempt in range(10):
                            body.send_keys(Keys.PAGE_DOWN)
                            time.sleep(0.5)
                            
                            key_urls = self.get_all_collection_urls_on_page()
                            key_new_count = len(set(key_urls) - all_urls)
                            all_urls.update(key_urls)
                            
                            if key_new_count > 0:
                                print(f"    ✅ Found {key_new_count} new URLs with PAGE_DOWN")
                                scroll_success = True
                                break
                    except Exception as e:
                        print(f"    ❌ Keyboard navigation failed: {e}")
                
                urls_after = len(all_urls)
                total_new = urls_after - urls_before
                
                if total_new > 0:
                    print(f"🔥 Total new URLs this round: {total_new} (Total: {urls_after})")
                    consecutive_no_new = 0
                else:
                    consecutive_no_new += 1
                    print(f"⚠️  No new URLs found ({consecutive_no_new}/3 strikes)")
                
                scroll_attempts += 1
                
                # Brief pause between scroll attempts
                time.sleep(1)
            
            # Final collection attempt
            print("\n🔍 Final URL sweep...")
            final_urls = self.get_all_collection_urls_on_page()
            final_new = len(set(final_urls) - all_urls)
            all_urls.update(final_urls)
            
            if final_new > 0:
                print(f"📦 Final sweep found {final_new} additional URLs")
            
            total_found = len(all_urls)
            print(f"\n📊 URL Collection Complete: {total_found} unique collection URLs found")
            return list(all_urls)
            
        except Exception as e:
            print(f"❌ Error during URL collection: {e}")
            return list(all_urls)

    def get_all_collection_urls_on_page(self) -> List[str]:
        """
        Get all collection URLs currently visible on the page
        
        Returns:
            List of unique collection URLs
        """
        try:
            # Get all collection links with multiple selectors
            collection_links = []
            
            selectors = [
                "[href*='/marketplace/collection/']",
                "a[href*='/marketplace/collection/']"
            ]
            
            for selector in selectors:
                try:
                    found_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    collection_links.extend(found_links)
                except:
                    continue
            
            urls = set()
            for link in collection_links:
                try:
                    href = link.get_attribute('href')
                    if href and '/marketplace/collection/' in href:
                        # Normalize URL (remove query params, fragments)
                        base_url = href.split('?')[0].split('#')[0]
                        urls.add(base_url)
                except:
                    continue
            
            return list(urls)
            
        except Exception as e:
            print(f"Error getting collection URLs: {e}")
            return []
    
    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nifty_gateway_items_{timestamp}.csv"
        
        if self.scraped_items:
            df = pd.DataFrame(self.scraped_items)
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
        else:
            print("No data to save")
    
    def save_to_json(self, filename: str = None):
        """Save scraped data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nifty_gateway_items_{timestamp}.json"
        
        if self.scraped_items:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_items, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        else:
            print("No data to save")
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Main function to run the scraper"""
    # URL for NiftyGateway Art NFTs sorted by most liked
    url = "https://www.niftygateway.com/explore/nfts/?sort=-likes&chain%5B0%5D=ethereum&categories=Art"
    
    # Create scraper instance
    with NiftyGatewayScraper(headless=False) as scraper:
        # Scrape items
        items = scraper.scrape_items(url, max_items=50, max_scrolls=10)
        
        # Save results
        if items:
            scraper.save_to_csv()
            scraper.save_to_json()
            
            # Print summary
            print(f"\n=== SCRAPING SUMMARY ===")
            print(f"Total items scraped: {len(items)}")
            print(f"Items with floor prices: {len([item for item in items if item['floor_price']])}")
            
            # Show first few items
            print(f"\n=== FIRST 5 ITEMS ===")
            for i, item in enumerate(items[:5], 1):
                print(f"{i}. {item['title']}")
                print(f"   Creator: {item['creator']}")
                print(f"   Floor Price: ${item['floor_price']}")
                print(f"   Contract: {item['contract']}")
                print(f"   Token ID: {item['token_id']}")
                print(f"   URL: {item['marketplace_url']}")
                print()
        else:
            print("No items were scraped")


if __name__ == "__main__":
    main()
