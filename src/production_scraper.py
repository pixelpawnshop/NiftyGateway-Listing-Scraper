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
    parser.add_argument('--no-opensea-enrichment', action='store_true',
                       help='Disable OpenSea collection name/slug enrichment')
    parser.add_argument('--no-arbitrage-analysis', action='store_true',
                       help='Disable arbitrage opportunity analysis')
    
    args = parser.parse_args()
    
    enable_opensea = not args.no_opensea_enrichment
    enable_arbitrage = not args.no_arbitrage_analysis
    
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
  OpenSea enrichment: {'Enabled' if enable_opensea else 'Disabled'}
  Arbitrage analysis: {'Enabled' if enable_arbitrage else 'Disabled'}
==========================================================
""")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize scraper with all options
    scraper = NiftyGatewayScraper(
        headless=args.headless, 
        enable_opensea_enrichment=enable_opensea,
        enable_arbitrage_analysis=enable_arbitrage
    )
    
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
                
                # Show OpenSea collection info if available
                if 'collection_name' in item:
                    print(f"  Collection Name: {item.get('collection_name', 'N/A')}")
                    print(f"  Collection Slug: {item.get('collection_slug', 'N/A')}")
                    if 'opensea_collection_url' in item:
                        print(f"  OpenSea Collection: {item['opensea_collection_url']}")
                
                # Show arbitrage analysis if available
                if 'arbitrage_flag' in item:
                    print(f"  Arbitrage Flag: {item.get('arbitrage_flag', 'N/A')}")
                    if item.get('opensea_offer_data'):
                        offer_data = item['opensea_offer_data']
                        quantity = offer_data.get('quantity', 1)
                        if quantity > 1:
                            print(f"  OpenSea Offer: {offer_data.get('offer_amount_eth', 0):.4f} ETH each (${offer_data.get('offer_amount_usd', 0):.2f} per item, {quantity}x quantity)")
                        else:
                            print(f"  OpenSea Offer: {offer_data.get('offer_amount_eth', 0):.4f} ETH (${offer_data.get('offer_amount_usd', 0):.2f})")
                        print(f"  Profit Potential: {item.get('profit_percentage', 0):+.1f}% (${item.get('potential_profit_usd', 0):+.2f})")
                    if 'opensea_item_url' in item:
                        print(f"  OpenSea Item: {item['opensea_item_url']}")
                
                print(f"  NiftyGateway URL: {item.get('marketplace_url', 'N/A')}")
                print(f"  Direct Item URL: {item.get('actual_marketplace_url', 'N/A')}")
            
            # Show arbitrage summary if analysis was enabled
            if enable_arbitrage:
                arbitrage_summary = {}
                for item in scraped_items:
                    flag = item.get('arbitrage_flag', 'Unknown')
                    arbitrage_summary[flag] = arbitrage_summary.get(flag, 0) + 1
                
                print(f"\n" + "="*50)
                print("ARBITRAGE ANALYSIS SUMMARY")
                print("="*50)
                for flag, count in sorted(arbitrage_summary.items()):
                    print(f"  {flag}: {count} items")
                
                # Highlight best opportunities
                excellent_opportunities = [item for item in scraped_items 
                                         if item.get('arbitrage_flag') == '🔥 RED']
                if excellent_opportunities:
                    print(f"\n🔥 EXCELLENT ARBITRAGE OPPORTUNITIES FOUND: {len(excellent_opportunities)}")
                    for opp in excellent_opportunities[:3]:  # Show top 3
                        profit_pct = opp.get('profit_percentage', 0)
                        profit_usd = opp.get('potential_profit_usd', 0)
                        print(f"   • {opp.get('collection_name', 'Unknown')} #{opp.get('actual_token_id')} - {profit_pct:+.1f}% (${profit_usd:+.2f})")
        
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
