import os

# Create necessary directories
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "constants.py"), exist_ok=True)

# Create constants.py file
constants_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "constants.py")
with open(constants_path, 'w') as f:
    f.write("""# Constants for MoneyPrinterV2
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

# Create config.py file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "config.py")
with open(config_path, 'w') as f:
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

# Create default config.json
config_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(config_json_path, 'w') as f:
    f.write("""{
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
      "enabled": true
    },
    "digital_products": {
      "enabled": true
    },
    "subscription": {
      "enabled": true
    }
  }
}""")

# Create __init__.py files for proper Python package structure
init_files = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "__init__.py"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "classes", "__init__.py"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "monetization", "__init__.py")
]

for init_file in init_files:
    with open(init_file, 'w') as f:
        f.write("# Package initialization\n")

print("Setup complete. MoneyPrinterV2 is ready to use!")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Configure your OpenAI API key in config.json")
print("3. Start the web UI: python app.py")
print("4. Access the Control Tower at http://localhost:5000")
