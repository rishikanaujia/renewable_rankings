"""Configuration loader for YAML files."""
import yaml
from pathlib import Path
from typing import Dict, Any
from functools import lru_cache


class ConfigLoader:
    """Load and manage YAML configuration files."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize config loader.
        
        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir)
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {config_dir}")
    
    @lru_cache(maxsize=10)
    def load(self, config_file: str) -> Dict[str, Any]:
        """Load a YAML configuration file.
        
        Args:
            config_file: Name of config file (e.g., 'app_config.yaml')
            
        Returns:
            Dictionary containing configuration
        """
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get_app_config(self) -> Dict[str, Any]:
        """Load main application configuration."""
        return self.load('app_config.yaml')
    
    def get_parameters(self) -> Dict[str, Any]:
        """Load parameter definitions."""
        return self.load('parameters.yaml')
    
    def get_weights(self) -> Dict[str, Any]:
        """Load subcategory weights."""
        return self.load('weights.yaml')
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Load UI configuration."""
        try:
            return self.load('ui_config.yaml')
        except FileNotFoundError:
            # Return defaults if file doesn't exist
            return {
                'theme': 'soft',
                'chat_history_limit': 50
            }

    def get_llm_config(self) -> Dict[str, Any]:
        """Load LLM configuration for AI-powered extraction.

        Returns configuration for AIExtractionAdapter including:
        - llm: LLM provider and model settings
        - cache: Cache configuration
        - document_processor: Document processing settings
        """
        try:
            return self.load('llm_config.yaml')
        except FileNotFoundError:
            # Return minimal defaults if file doesn't exist
            import os
            return {
                'llm': {
                    'provider': os.getenv('LLM_PROVIDER', 'anthropic'),
                    'model_name': os.getenv('LLM_MODEL', 'claude-3-5-sonnet-20241022'),
                    'temperature': 0.1,
                    'max_tokens': 4000,
                    'max_retries': 3
                },
                'cache': {
                    'enabled': True,
                    'ttl': 86400
                }
            }


# Global config loader instance
config_loader = ConfigLoader()
