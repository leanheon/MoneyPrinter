# Configuration module for MoneyPrinterV2
import os
import json
from src.constants import ROOT_DIR

def get_config():
    """
    Load configuration from config.json
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = os.path.join(ROOT_DIR, "config.json")
    
    if not os.path.exists(config_path):
        # Create default config
        config = {
            "openai": {
                "api_key": "",
                "model": "gpt-4-turbo"
            },
            "monetization": {
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
        }
        
        # Save default config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config
    
    # Load existing config
    with open(config_path, 'r') as f:
        return json.load(f)
