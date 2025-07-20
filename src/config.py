import json
import os

from src.constants import ROOT_DIR


def get_config():
    """Load configuration from the project's config.json."""
    config_path = os.path.join(ROOT_DIR, "config.json")

    if not os.path.exists(config_path):
        # If the configuration file is missing, return an empty dict
        # so that modules depending on configuration can still initialize.
        return {}

    with open(config_path, "r") as f:
        return json.load(f)
