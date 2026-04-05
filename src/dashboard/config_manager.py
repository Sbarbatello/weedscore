"""
Configuration manager for Weedscore user preferences.
Handles loading and saving UserPreferences to config/preferences.json.
"""

import os
import json
from pathlib import Path
from src.engine.models import UserPreferences

CONFIG_DIR = Path("config")
CONFIG_FILE = CONFIG_DIR / "preferences.json"

def load_preferences() -> UserPreferences:
    """
    Loads user preferences from config/preferences.json or returns defaults.
    """
    if not CONFIG_FILE.exists():
        return UserPreferences()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return UserPreferences(**data)
    except (json.JSONDecodeError, ValueError):
        # Fallback to defaults on corrupt config
        return UserPreferences()

def save_preferences(prefs: UserPreferences) -> None:
    """
    Saves user preferences to config/preferences.json.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(prefs.model_dump_json(indent=4))
