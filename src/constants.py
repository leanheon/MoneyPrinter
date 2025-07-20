# Constants for MoneyPrinterV2
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
