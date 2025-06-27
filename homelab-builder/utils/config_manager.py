#!/usr/bin/env python3
"""
Configuration Manager
Handles saving and loading configuration files.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class ConfigManager:
    """Manages configuration files for the homelab."""
    
    def __init__(self):
        self.config_dir = Path("/opt/homelab/configs")
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save_config(self, config: Dict[str, Any], filename: str = "homelab_config.json") -> str:
        """Save configuration to file."""
        config_path = self.config_dir / filename
        
        # Add metadata
        config['_metadata'] = {
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        # Save as JSON
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure permissions
        os.chmod(config_path, 0o600)
        
        return str(config_path)
    
    def load_config(self, filename: str = "homelab_config.json") -> Optional[Dict[str, Any]]:
        """Load configuration from file."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            return None
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def save_yaml_config(self, config: Dict[str, Any], filename: str) -> str:
        """Save configuration as YAML."""
        config_path = self.config_dir / filename
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return str(config_path)
    
    def load_yaml_config(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load YAML configuration."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            return None
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def list_configs(self) -> List[str]:
        """List all configuration files."""
        configs = []
        for file in self.config_dir.iterdir():
            if file.suffix in ['.json', '.yml', '.yaml']:
                configs.append(file.name)
        return configs
    
    def backup_config(self, filename: str) -> str:
        """Create a backup of a configuration file."""
        config_path = self.config_dir / filename
        if not config_path.exists():
            raise FileNotFoundError(f"Config file {filename} not found")
        
        backup_name = f"{config_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{config_path.suffix}"
        backup_path = self.config_dir / "backups" / backup_name
        backup_path.parent.mkdir(exist_ok=True)
        
        import shutil
        shutil.copy2(config_path, backup_path)
        
        return str(backup_path)
