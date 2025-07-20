import json
import os
from src.constants import ROOT_DIR


def get_config():
    """Load configuration from config.json located at project root."""
    config_path = os.path.join(ROOT_DIR, "config.json")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return json.load(f)
