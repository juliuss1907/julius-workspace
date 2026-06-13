"""
Configuration Loader
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self._default_params = None
        self._thresholds = None
        self._coin_params = {}
    
    def load_default_params(self) -> Dict[str, Any]:
        """Load default parameters"""
        if self._default_params is None:
            config_file = self.config_dir / "default_params.yaml"
            with open(config_file) as f:
                self._default_params = yaml.safe_load(f)
        return self._default_params
    
    def load_thresholds(self) -> Dict[str, Any]:
        """Load risk thresholds"""
        if self._thresholds is None:
            config_file = self.config_dir / "thresholds.yaml"
            with open(config_file) as f:
                self._thresholds = yaml.safe_load(f)
        return self._thresholds
    
    def load_coin_params(self, coin: str) -> Dict[str, Any]:
        """Load coin-specific parameters (inherits from default)"""
        if coin not in self._coin_params:
            # Load default first
            params = self.load_default_params().copy()
            
            # Try to load coin-specific overrides
            coin_file = self.config_dir / "coin_params" / f"{coin}.yaml"
            if coin_file.exists():
                with open(coin_file) as f:
                    coin_overrides = yaml.safe_load(f)
                    # Deep merge (simple version)
                    params = self._deep_merge(params, coin_overrides)
            
            self._coin_params[coin] = params
        
        return self._coin_params[coin]
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dicts"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_param(self, path: str, coin: Optional[str] = None, default: Any = None) -> Any:
        """Get parameter by dot notation path
        
        Example: config.get_param('risk_management.risk_per_trade', 'BTC')
        """
        if coin:
            params = self.load_coin_params(coin)
        else:
            params = self.load_default_params()
        
        keys = path.split('.')
        value = params
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value


# Global config instance
config = Config()
