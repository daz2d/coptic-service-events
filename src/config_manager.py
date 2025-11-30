"""Configuration manager"""

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'location.zip_code')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set config value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def validate(self) -> bool:
        """Validate required configuration"""
        # Check if location is configured
        if not self.get('location.use_current_location'):
            if not self.get('location.zip_code'):
                raise ValueError("Either zip_code or use_current_location must be set")
        
        return True
