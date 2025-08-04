"""
Discord notification system for arbitrage opportunities
Sends alerts when profitable NFT arbitrage opportunities are found
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        """
        Initialize Discord notifier with webhook URL
        
        Args:
            webhook_url: Discord webhook URL for sending messages
        """
        self.webhook_url = webhook_url
        
    def send_arbitrage_alert(self, item_data: Dict[str, Any]) -> bool:
        """
        Send arbitrage opportunity alert to Discord
        
        Args:
            item_data: Item data with arbitrage information
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Only send alerts for profitable opportunities
            arbitrage_flag = item_data.get('arbitrage_flag', '')
            if arbitrage_flag not in ['🔥 RED', '🟡 YELLOW', '🟢 GREEN']:
                return False
            
            # Build the Discord embed message
            embed = self._build_arbitrage_embed(item_data)
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 204:
                print(f"🚀 Discord alert sent: {arbitrage_flag} opportunity")
                return True
            else:
                print(f"❌ Discord notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Discord notification error: {e}")
            return False
    
    def _build_arbitrage_embed(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Discord embed for arbitrage opportunity
        
        Args:
            item_data: Item data with arbitrage information
            
        Returns:
            Discord embed dictionary
        """
        arbitrage_flag = item_data.get('arbitrage_flag', '')
        profit_percentage = item_data.get('profit_percentage', 0)
        potential_profit_usd = item_data.get('potential_profit_usd', 0)
        collection_name = item_data.get('collection_name', 'Unknown Collection')
        token_id = item_data.get('actual_token_id', 'Unknown')
        floor_price = item_data.get('floor_price', 0)
        
        # OpenSea offer data
        offer_data = item_data.get('opensea_offer_data', {})
        offer_eth = offer_data.get('offer_amount_eth', 0)
        offer_usd = offer_data.get('offer_amount_usd', 0)
        quantity = offer_data.get('quantity', 1)
        
        # URLs
        nifty_url = item_data.get('actual_marketplace_url', '')
        opensea_url = item_data.get('opensea_item_url', '')
        
        # Set embed color based on opportunity level
        colors = {
            '🔥 RED': 0xFF0000,    # Red
            '🟡 YELLOW': 0xFFFF00, # Yellow  
            '🟢 GREEN': 0x00FF00   # Green
        }
        color = colors.get(arbitrage_flag, 0x808080)
        
        # Build title and description
        title = f"{arbitrage_flag} ARBITRAGE OPPORTUNITY"
        
        description = f"**{collection_name}** #{token_id}\n"
        description += f"💰 **Profit: ${potential_profit_usd:+.2f} ({profit_percentage:+.1f}%)**\n\n"
        
        # Price comparison
        description += f"📈 **NiftyGateway**: ${floor_price:.2f}\n"
        description += f"📊 **OpenSea Offer**: {offer_eth:.4f} ETH (${offer_usd:.2f})"
        
        if quantity > 1:
            description += f" - {quantity}x quantity"
        
        description += "\n\n"
        
        # Opportunity explanation  
        if arbitrage_flag == '🔥 RED':
            description += "🚀 **INSTANT PROFIT** - OpenSea offer >= Nifty price!"
        elif arbitrage_flag == '🟡 YELLOW':
            description += "⚡ **STRONG OPPORTUNITY** - Within 10% of Nifty price"
        elif arbitrage_flag == '🟢 GREEN':
            description += "💡 **MODERATE OPPORTUNITY** - Within 20% of Nifty price"
        
        # Build embed
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "🛒 Buy on NiftyGateway",
                    "value": f"[View Item]({nifty_url})",
                    "inline": True
                },
                {
                    "name": "💎 Sell on OpenSea", 
                    "value": f"[View Item]({opensea_url})",
                    "inline": True
                },
                {
                    "name": "📊 Collection",
                    "value": f"[{collection_name}]({item_data.get('opensea_collection_url', '')})",
                    "inline": False
                }
            ],
            "footer": {
                "text": "NiftyGateway Arbitrage Bot",
                "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            }
        }
        
        return embed
    
    def send_startup_message(self) -> bool:
        """
        Send bot startup notification to Discord
        
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            embed = {
                "title": "🤖 Arbitrage Scanner Started",
                "description": "NiftyGateway arbitrage opportunity scanner is now active!\n\nWatching for:\n🔥 **RED** - Instant profit opportunities\n🟡 **YELLOW** - Strong arbitrage potential\n🟢 **GREEN** - Moderate opportunities",
                "color": 0x00FF00,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "NiftyGateway Arbitrage Bot"
                }
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"❌ Startup notification error: {e}")
            return False
    
    def send_summary_message(self, total_processed: int, opportunities_found: int, red_flags: int, yellow_flags: int, green_flags: int) -> bool:
        """
        Send scanning session summary to Discord
        
        Args:
            total_processed: Total items processed
            opportunities_found: Total opportunities found
            red_flags: Number of red flag opportunities
            yellow_flags: Number of yellow flag opportunities  
            green_flags: Number of green flag opportunities
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            description = f"**Scanning Session Complete**\n\n"
            description += f"📊 **Items Processed**: {total_processed:,}\n"
            description += f"💎 **Opportunities Found**: {opportunities_found}\n\n"
            
            if opportunities_found > 0:
                description += f"🔥 **RED (Excellent)**: {red_flags}\n"
                description += f"🟡 **YELLOW (Good)**: {yellow_flags}\n"
                description += f"🟢 **GREEN (Fair)**: {green_flags}\n"
            else:
                description += "No arbitrage opportunities found this scan."
            
            embed = {
                "title": "📈 Scanning Summary",
                "description": description,
                "color": 0x0099FF,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "NiftyGateway Arbitrage Bot"
                }
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"❌ Summary notification error: {e}")
            return False
