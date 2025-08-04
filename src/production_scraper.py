"""
Production arbitrage scanner for NiftyGateway NFT marketplace
Real-time Discord notifications for arbitrage opportunities
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from nifty_scraper import NiftyGatewayScraper
from discord_notifier import DiscordNotifier
import config

# Discord webhook URL for arbitrage alerts
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1401964079651754076/dQVdnPAIdyBI4NUIh8ISmJr7uGqp4-Hhk264Y5y8j5IqfK-I_V9PzA7yAmGA8WDVcv2k"

def main():
    parser = argparse.ArgumentParser(description='NiftyGateway Arbitrage Scanner with Discord Alerts')
    parser.add_argument('--max-items', type=int, default=0, 
                       help='Maximum number of items to scan (0 = unlimited, default: unlimited)')
    parser.add_argument('--headless', action='store_true', 
                       help='Run browser in headless mode (recommended for production)')
    parser.add_argument('--start-url', type=str, default=config.BASE_URL,
                       help='Starting URL for scanning (default from config)')
    parser.add_argument('--max-scrolls', type=int, default=50,
                       help='Maximum number of scroll attempts (default: 50)')
    parser.add_argument('--no-opensea-enrichment', action='store_true',
                       help='Disable OpenSea collection name/slug enrichment')
    parser.add_argument('--no-arbitrage-analysis', action='store_true',
                       help='Disable arbitrage opportunity analysis')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously, rescanning after completion')
    parser.add_argument('--scan-interval', type=int, default=10,
                       help='Interval between scans in continuous mode (seconds, default: 10)')
    
    args = parser.parse_args()
    
    enable_opensea = not args.no_opensea_enrichment
    enable_arbitrage = not args.no_arbitrage_analysis
    
    if not enable_arbitrage:
        print("❌ Error: Arbitrage analysis must be enabled for Discord notifications!")
        print("   This scanner is designed to find arbitrage opportunities.")
        sys.exit(1)
    
    # Initialize Discord notifier
    discord = DiscordNotifier(DISCORD_WEBHOOK_URL)
    
    print(f"""
==========================================================
    🤖 NiftyGateway Arbitrage Scanner
==========================================================
Mode: REAL-TIME Discord alerts for arbitrage opportunities
Configuration:
  Max items: {'Unlimited' if args.max_items == 0 else args.max_items}
  Headless mode: {args.headless}
  Starting URL: {args.start_url}
  Max scrolls: {args.max_scrolls}
  OpenSea enrichment: {'Enabled' if enable_opensea else 'Disabled'}
  Arbitrage analysis: {'Enabled' if enable_arbitrage else 'Disabled'}
  Continuous mode: {'Enabled' if args.continuous else 'Disabled'}
  
🎯 Watching for: 🔥 RED, 🟡 YELLOW, 🟢 GREEN opportunities
💬 Discord alerts: INSTANT (sent as soon as found)
==========================================================
""")
    
    # Send startup notification to Discord
    print("📡 Sending startup notification to Discord...")
    discord.send_startup_message()
    
    # Define real-time callback for immediate Discord notifications
    def arbitrage_callback(item_data):
        """Send immediate Discord notification when arbitrage opportunity is found"""
        arbitrage_flag = item_data.get('arbitrage_flag', '')
        if arbitrage_flag in ['🔥 RED', '🟡 YELLOW', '🟢 GREEN']:
            discord.send_arbitrage_alert(item_data)
            
            # Console notification
            collection_name = item_data.get('collection_name', 'Unknown')
            token_id = item_data.get('actual_token_id', 'Unknown')
            profit_pct = item_data.get('profit_percentage', 0)
            profit_usd = item_data.get('potential_profit_usd', 0)
            
            print(f"🚨 REAL-TIME ALERT: {arbitrage_flag} - {collection_name} #{token_id} - {profit_pct:+.1f}% (${profit_usd:+.2f})")
    
    # Initialize scraper with real-time callback
    scraper = NiftyGatewayScraper(
        headless=args.headless, 
        enable_opensea_enrichment=enable_opensea,
        enable_arbitrage_analysis=enable_arbitrage,
        arbitrage_callback=arbitrage_callback
    )
    
    # Opportunity counters
    session_opportunities = 0
    session_red = 0
    session_yellow = 0 
    session_green = 0
    total_processed = 0
    
    try:
        print(f"🚀 Starting arbitrage scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        while True:  # Main scanning loop
            # Run the scraper
            max_items_to_use = None if args.max_items == 0 else args.max_items
            scraped_items = scraper.scrape_items(
                url=args.start_url,
                max_items=max_items_to_use or 999999,  # Use large number if unlimited
                max_scrolls=args.max_scrolls
            )
            
            if scraped_items:
                total_processed += len(scraped_items)
                scan_opportunities = 0
                scan_red = 0
                scan_yellow = 0
                scan_green = 0
                
                # Count opportunities that were already sent via real-time callback
                for item in scraped_items:
                    arbitrage_flag = item.get('arbitrage_flag', '')
                    
                    # Count by flag type (notifications already sent via callback)
                    if arbitrage_flag in ['🔥 RED', '🟡 YELLOW', '🟢 GREEN']:
                        scan_opportunities += 1
                        session_opportunities += 1
                        
                        if arbitrage_flag == '🔥 RED':
                            scan_red += 1
                            session_red += 1
                        elif arbitrage_flag == '🟡 YELLOW':
                            scan_yellow += 1
                            session_yellow += 1
                        elif arbitrage_flag == '🟢 GREEN':
                            scan_green += 1
                            session_green += 1
                
                print(f"""
==========================================================
    Scan Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==========================================================
📊 Items Processed: {len(scraped_items)}
💎 Opportunities Found: {scan_opportunities}
🔥 RED (Excellent): {scan_red}
🟡 YELLOW (Good): {scan_yellow}  
🟢 GREEN (Fair): {scan_green}
==========================================================
""")
                
                # Send summary to Discord
                discord.send_summary_message(
                    total_processed=len(scraped_items),
                    opportunities_found=scan_opportunities,
                    red_flags=scan_red,
                    yellow_flags=scan_yellow,
                    green_flags=scan_green
                )
                
            else:
                print("❌ No items were processed. Please check the configuration and try again.")
            
            # Break if not continuous mode
            if not args.continuous:
                break
            else:
                print(f"🔄 Continuous mode enabled - waiting {args.scan_interval} seconds before next scan...")
                time.sleep(args.scan_interval)
                
    except KeyboardInterrupt:
        print(f"\n⏹️  Scanning interrupted by user.")
        print(f"📊 Session Summary:")
        print(f"   Total processed: {total_processed}")
        print(f"   Opportunities found: {session_opportunities}")
        if session_opportunities > 0:
            print(f"   🔥 RED: {session_red}, 🟡 YELLOW: {session_yellow}, 🟢 GREEN: {session_green}")
        
    except Exception as e:
        print(f"\n❌ Error during scanning: {str(e)}")
        
    finally:
        # Always close the scraper
        scraper.close()
        print("🔧 Scanner closed.")

if __name__ == "__main__":
    main()
