import os

# Constants for MoneyPrinterV2

# Root directory of the repository
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application version
VERSION = "2.0.0"

# Supported platforms for content generation/posting
PLATFORMS = ["youtube", "twitter", "threads"]

# Default content types by platform
CONTENT_TYPES = {
    "youtube": ["video", "shorts"],
    "twitter": ["post", "thread"],
    "threads": ["post", "carousel"],
}
