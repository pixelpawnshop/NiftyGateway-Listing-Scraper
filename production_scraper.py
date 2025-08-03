"""
Production scraper for NiftyGateway NFT marketplace
Optimized for large-scale data collection
"""

import os
import sys
import json
import argparse
from datetime import datetime
from nifty_scraper import NiftyGatewayScraper
import config

def main():
    parser = argparse.ArgumentParser(description='NiftyGateway NFT Scraper')
    parser.add_argument('--max-items', type=int, default=1000, 
                       help='Maximum number of items to scrape (0 = unlimited, default: 1000)')
    parser.add_argument('--headless', action='store_true', 
                       help='Run browser in headless mode (recommended for production)')
    parser.add_argument('--output-dir', type=str, default='.', 
                       help='Output directory for data files (default: current directory)')
    parser.add_argument('--start-url', type=str, default=config.BASE_URL,
                       help='Starting URL for scraping (default from config)')
    parser.add_argument('--max-scrolls', type=int, default=50,
                       help='Maximum number of scroll attempts (default: 50)')
    
    args = parser.parse_args()
    
    print(f"""
==========================================================
    NiftyGateway NFT Production Scraper
==========================================================
Configuration:
  Max items: {'Unlimited' if args.max_items == 0 else args.max_items}
  Headless mode: {args.headless}
  Output directory: {args.output_dir}
  Starting URL: {args.start_url}
  Max scrolls: {args.max_scrolls}
==========================================================
""")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize scraper
    scraper = NiftyGatewayScraper(headless=args.headless)
    
    try:
        print(f"Starting scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the scraper
        max_items_to_use = None if args.max_items == 0 else args.max_items
        scraped_items = scraper.scrape_items(
            url=args.start_url,
            max_items=max_items_to_use or 999999,  # Use large number if unlimited
            max_scrolls=args.max_scrolls
        )
        
        if scraped_items:
            # Generate filenames with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save to JSON
            json_filename = os.path.join(args.output_dir, f"nifty_gateway_items_{timestamp}.json")
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(scraped_items, f, indent=2, ensure_ascii=False)
            
            # Save to CSV
            csv_filename = os.path.join(args.output_dir, f"nifty_gateway_items_{timestamp}.csv")
            scraper.save_to_csv(csv_filename)
            
            print(f"""
==========================================================
    Scraping Completed Successfully!
==========================================================
Results:
  Items scraped: {len(scraped_items)}
  Files saved:
    - JSON: {json_filename}
    - CSV: {csv_filename}
  
  Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==========================================================
""")
            
            # Show some sample data
            print("Sample of scraped data:")
            for i, item in enumerate(scraped_items[:3]):
                print(f"\nItem {i+1}:")
                print(f"  Floor Price: ${item.get('floor_price', 'N/A')}")
                print(f"  Token ID: #{item.get('actual_token_id', 'N/A')}")
                print(f"  Contract: {item.get('contract', 'N/A')}")
                print(f"  Collection URL: {item.get('marketplace_url', 'N/A')}")
        
        else:
            print("No items were scraped. Please check the configuration and try again.")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
        
    except Exception as e:
        print(f"\nError during scraping: {str(e)}")
        
    finally:
        # Always close the scraper
        scraper.close()
        print("\nScraper closed.")

if __name__ == "__main__":
    main()
