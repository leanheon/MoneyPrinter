import os
import json
from src.monetization.affiliate import AffiliateManager
from src.monetization.sponsorship import SponsorshipManager
from src.monetization.digital_products import DigitalProductManager
from src.monetization.subscription import SubscriptionManager
from src.config import get_config
from src.constants import ROOT_DIR

class MonetizationManager:
    """
    Main class for managing all monetization features
    """
    def __init__(self):
        """
        Initialize the MonetizationManager with all monetization components
        """
        # Create monetization directory if it doesn't exist
        self.monetization_dir = os.path.join(ROOT_DIR, ".mp", "monetization")
        os.makedirs(self.monetization_dir, exist_ok=True)
        
        # Initialize configuration
        self._init_config()
        
        # Initialize monetization components
        self.affiliate_manager = AffiliateManager()
        self.sponsorship_manager = SponsorshipManager()
        self.digital_product_manager = DigitalProductManager()
        self.subscription_manager = SubscriptionManager()
        
    def _init_config(self):
        """
        Initialize monetization configuration
        """
        config = get_config()
        
        # Check if monetization config exists
        if "monetization" not in config:
            config["monetization"] = {
                "affiliate": {
                    "amazon_tag": "",
                    "clickbank_id": ""
                },
                "sponsorship": {
                    "enabled": True
                },
                "digital_products": {
                    "enabled": True
                },
                "subscription": {
                    "enabled": True
                }
            }
            
            # Save updated config
            config_file = os.path.join(ROOT_DIR, "config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
    def generate_monetized_content(self, topic, platform, monetization_type=None):
        """
        Generate content with monetization based on topic and platform
        
        Args:
            topic (str): Content topic
            platform (str): Platform (youtube, twitter, threads)
            monetization_type (str, optional): Specific monetization type to use
            
        Returns:
            dict: Generated content with monetization
        """
        # If monetization type is specified, use that specific method
        if monetization_type:
            if monetization_type == "affiliate":
                return self.affiliate_manager.generate_affiliate_content(topic, platform)
            elif monetization_type == "sponsorship":
                return self.sponsorship_manager.generate_sponsored_content(topic, platform)
            elif monetization_type == "digital_product":
                # First check if we have relevant products
                products = self.digital_product_manager.get_products()
                if products:
                    # Use an existing product
                    product_id = products[0]["product_id"]
                    return self.digital_product_manager.generate_product_promotion(product_id, platform)
                else:
                    # Create a new product and then promote it
                    product_type = "guide" if platform == "youtube" else "checklist"
                    product = self.digital_product_manager.generate_digital_product(topic, product_type)
                    if product:
                        return self.digital_product_manager.generate_product_promotion(product["product_id"], platform)
            elif monetization_type == "subscription":
                # Promote the premium tier by default
                return self.subscription_manager.generate_tier_promotion("premium", platform)
        
        # If no specific type is specified, choose the best method based on topic and platform
        # This is a simple implementation - could be enhanced with AI
        if platform == "youtube":
            # YouTube works well with affiliate marketing and digital products
            if "review" in topic.lower() or "best" in topic.lower():
                return self.affiliate_manager.generate_affiliate_content(topic, platform)
            elif "how to" in topic.lower() or "guide" in topic.lower():
                # Create and promote a digital product
                product = self.digital_product_manager.generate_digital_product(topic, "guide")
                if product:
                    return self.digital_product_manager.generate_product_promotion(product["product_id"], platform)
            else:
                # Default to sponsorship for other topics
                return self.sponsorship_manager.generate_sponsored_content(topic, platform)
        elif platform == "twitter" or platform == "threads":
            # Social media works well with short-form affiliate links and subscription promotions
            if "deal" in topic.lower() or "sale" in topic.lower():
                return self.affiliate_manager.generate_affiliate_content(topic, platform)
            elif "exclusive" in topic.lower() or "community" in topic.lower():
                return self.subscription_manager.generate_tier_promotion("premium", platform)
            else:
                # Default to sponsorship for other topics
                return self.sponsorship_manager.generate_sponsored_content(topic, platform)
        
        # Default to affiliate marketing if no specific match
        return self.affiliate_manager.generate_affiliate_content(topic, platform)
    
    def get_monetization_stats(self):
        """
        Get statistics for all monetization methods
        
        Returns:
            dict: Monetization statistics
        """
        stats = {
            "affiliate": {
                "programs": len(self.affiliate_manager.affiliate_programs),
                "products": sum(len(program["products"]) for program in self.affiliate_manager.affiliate_programs.values())
            },
            "sponsorship": {
                "brands": len(self.sponsorship_manager.brands),
                "campaigns": len(self.sponsorship_manager.campaigns)
            },
            "digital_products": {
                "products": len(self.digital_product_manager.products)
            },
            "subscription": {
                "tiers": len(self.subscription_manager.tiers),
                "members": len(self.subscription_manager.members),
                "content": len(self.subscription_manager.content)
            }
        }
        
        return stats
    
    def get_revenue_estimate(self):
        """
        Get estimated revenue from all monetization methods
        
        Returns:
            dict: Estimated revenue
        """
        # This is a simplified estimation model
        # In a real implementation, this would be based on actual data
        
        # Affiliate revenue estimate
        affiliate_products = sum(len(program["products"]) for program in self.affiliate_manager.affiliate_programs.values())
        affiliate_revenue = affiliate_products * 10  # Assume $10 per product on average
        
        # Sponsorship revenue estimate
        sponsorship_revenue = sum(float(campaign.get("budget", 0)) for campaign in self.sponsorship_manager.campaigns.values())
        
        # Digital products revenue estimate
        product_revenue = sum(float(product.get("price", 0)) * int(product.get("sales_count", 0)) 
                             for product in self.digital_product_manager.products.values())
        
        # Subscription revenue estimate
        subscription_revenue = sum(float(self.subscription_manager.tiers.get(member.get("tier_id", ""), {}).get("price", 0)) 
                                  for member in self.subscription_manager.members.values() 
                                  if member.get("status") == "active")
        
        return {
            "affiliate": affiliate_revenue,
            "sponsorship": sponsorship_revenue,
            "digital_products": product_revenue,
            "subscription": subscription_revenue,
            "total": affiliate_revenue + sponsorship_revenue + product_revenue + subscription_revenue
        }
