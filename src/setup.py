import os
import sys
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create necessary directories
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".mp"), exist_ok=True)

# Create a basic config file if it doesn't exist
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
if not os.path.exists(config_path):
    config = {
        "openai": {
            "api_key": "YOUR_OPENAI_API_KEY_HERE",
            "model": "gpt-4-turbo"
        },
        "monetization": {
            "affiliate": {
                "amazon_tag": "moneyprinter-20",
                "clickbank_id": "moneyprinter"
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
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Created config file at {config_path}")
    print("Please update the OpenAI API key in the config file before running tests.")

# Create constants.py if it doesn't exist
constants_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "constants.py")
os.makedirs(os.path.dirname(constants_path), exist_ok=True)
if not os.path.exists(constants_path):
    with open(constants_path, 'w') as f:
        f.write(f"""# Constants for MoneyPrinterV2
import os

# Root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Version
VERSION = "2.0.0"

# Supported platforms
PLATFORMS = ["youtube", "twitter", "threads"]

# Default content types
CONTENT_TYPES = {
    "youtube": ["video", "shorts"],
    "twitter": ["post", "thread"],
    "threads": ["post", "carousel"]
}
""")
    print(f"Created constants file at {constants_path}")

# Create config.py if it doesn't exist
config_module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "config.py")
if not os.path.exists(config_module_path):
    with open(config_module_path, 'w') as f:
        f.write("""# Configuration module for MoneyPrinterV2
import os
import json
from src.constants import ROOT_DIR

def get_config():
    \"\"\"
    Load configuration from config.json
    
    Returns:
        dict: Configuration dictionary
    \"\"\"
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
""")
    print(f"Created config module at {config_module_path}")

print("Setup complete. You can now run the test_monetization.py script.")
