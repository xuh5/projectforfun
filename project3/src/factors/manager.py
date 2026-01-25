"""Factor manager for coordinating multiple factor providers."""

import importlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from .registry import FactorRegistry
from .base import FactorProvider

logger = logging.getLogger(__name__)


class FactorManager:
    """Manages factor providers and coordinates factor fetching."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize factor manager.
        
        Args:
            config_path: Path to factor configuration JSON file.
                        If None, uses default config or creates one.
        """
        self.registry = FactorRegistry()
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self._providers_initialized = False
        
        logger.info(f"FactorManager initialized with config: {self.config_path}")
    
    def _get_default_config_path(self) -> Path:
        """Get default config file path."""
        # Look for config in factors directory
        factors_dir = Path(__file__).parent
        config_file = factors_dir / "factor_config.json"
        return config_file
    
    def _load_config(self) -> dict:
        """
        Load configuration from JSON file.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded factor configuration from {self.config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                logger.info("Using default configuration")
        
        # Default configuration
        return {
            "provider_registry": {
                "yfinance": {
                    "module": "factors.first_level.yfinance_fetcher",
                    "class": "YFinanceFactorFetcher"
                }
            },
            "enabled_providers": ["yfinance"],
            "factor_selection": {
                "yfinance": []
            },
            "provider_config": {
                "yfinance": {
                    "factors_dir": "factors",
                    "delay": 1.5
                }
            }
        }
    
    def initialize_providers(self) -> None:
        """Initialize and register providers based on configuration."""
        if self._providers_initialized:
            logger.debug("Providers already initialized")
            return
        
        enabled = self.config.get("enabled_providers", [])
        provider_config = self.config.get("provider_config", {})
        
        for provider_name in enabled:
            try:
                provider = self._create_provider(provider_name, provider_config.get(provider_name, {}))
                if provider:
                    self.registry.register(provider)
                    logger.info(f"Initialized provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to initialize provider '{provider_name}': {e}")
                continue
        
        self._providers_initialized = True
        logger.info(f"Initialized {len(self.registry)} provider(s)")
    
    def _create_provider(self, name: str, config: dict) -> Optional[FactorProvider]:
        """
        Create a provider instance based on name.
        Dynamically imports from provider_registry in config.
        
        Args:
            name: Provider name
            config: Provider-specific configuration
            
        Returns:
            FactorProvider instance or None
        """
        # Get provider registry from config
        provider_registry = self.config.get("provider_registry", {})
        
        if name not in provider_registry:
            logger.warning(f"Provider '{name}' not found in provider_registry")
            return None
        
        provider_info = provider_registry[name]
        module_path = provider_info.get("module")
        class_name = provider_info.get("class")
        
        if not module_path or not class_name:
            logger.error(f"Provider '{name}' missing 'module' or 'class' in registry")
            return None
        
        try:
            # Dynamic import
            # Handle relative imports (factors.first_level.xxx)
            if module_path.startswith("factors."):
                # Convert to relative import
                # factors.first_level.yfinance_fetcher -> .first_level.yfinance_fetcher
                relative_path = module_path.replace("factors.", ".")
                module = importlib.import_module(relative_path, package="factors")
            else:
                # Absolute import
                module = importlib.import_module(module_path)
            
            # Get the class
            provider_class = getattr(module, class_name)
            
            # Create instance with config
            return provider_class(**config)
            
        except ImportError as e:
            logger.error(f"Failed to import module '{module_path}' for provider '{name}': {e}")
            return None
        except AttributeError as e:
            logger.error(f"Class '{class_name}' not found in module '{module_path}' for provider '{name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create provider '{name}': {e}")
            return None
    
    def fetch_all_factors(self, symbols: List[str], **kwargs) -> Dict[str, Dict]:
        """
        Fetch factors from all enabled providers and merge results.
        
        Args:
            symbols: List of stock symbols
            **kwargs: Additional parameters to pass to providers
            
        Returns:
            Dictionary mapping symbol to merged factor data
        """
        if not self._providers_initialized:
            self.initialize_providers()
        
        enabled = self.config.get("enabled_providers", [])
        factor_selection = self.config.get("factor_selection", {})
        
        all_factors: Dict[str, Dict] = {symbol: {} for symbol in symbols}
        
        for provider_name in enabled:
            provider = self.registry.get_provider(provider_name)
            if not provider:
                logger.warning(f"Provider '{provider_name}' not found")
                continue
            
            try:
                provider_factors = provider.fetch_factors(symbols, **kwargs)
                selected = factor_selection.get(provider_name, [])
                
                for symbol, factors in provider_factors.items():
                    if selected:
                        all_factors[symbol].update(
                            provider.extract_factors(factors, set(selected))
                        )
                    else:
                        all_factors[symbol].update(factors)
                
                logger.info(f"✓ {provider_name}: {len(provider_factors)} symbols")
            except Exception as e:
                logger.error(f"Failed {provider_name}: {e}")
        
        return all_factors
    
    def get_available_factors(self) -> Set[str]:
        """
        Get all available factors from enabled providers.
        
        Returns:
            Set of all available factor names
        """
        if not self._providers_initialized:
            self.initialize_providers()
        
        enabled = self.config.get("enabled_providers", [])
        factor_selection = self.config.get("factor_selection", {})
        
        all_factors = set()
        
        for provider_name in enabled:
            provider = self.registry.get_provider(provider_name)
            if not provider:
                continue
            
            selected_factors = factor_selection.get(provider_name, [])
            if selected_factors:
                # Only include selected factors
                all_factors.update(selected_factors)
            else:
                # Include all available factors from provider
                all_factors.update(provider.get_available_factors())
        
        return all_factors
    
    def get_factors_by_provider(self, provider_name: str) -> Optional[Set[str]]:
        """
        Get factors available from a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Set of factor names or None if provider not found
        """
        return self.registry.get_factors_by_provider(provider_name)
    
    def list_enabled_providers(self) -> List[str]:
        """
        List all enabled provider names.
        
        Returns:
            List of enabled provider names
        """
        return self.config.get("enabled_providers", [])
    
    def save_factors_excel(self, factors_data: Dict[str, Dict], stocks_data: List[Dict], output_file: str = "filtered_stocks_with_factors.xlsx") -> None:
        """
        Save filtered stocks with all factors to Excel file.
        
        Args:
            factors_data: Dictionary mapping symbol to factor data
            stocks_data: List of stock dictionaries (with symbol, name, sector, etc.)
            output_file: Output Excel filename
        """
        try:
            import pandas as pd
            from pathlib import Path
            
            # Prepare data for Excel
            excel_data = []
            for stock in stocks_data:
                symbol = stock.get("symbol")
                if symbol not in factors_data:
                    continue
                
                # Start with basic stock info
                row = {
                    "Symbol": symbol,
                    "Company Name": stock.get("name", ""),
                    "Sector": stock.get("sector", ""),
                    "Industry": stock.get("industry", ""),
                }
                
                # Add all factors
                factors = factors_data[symbol]
                for key, value in factors.items():
                    if key not in ["symbol", "ticker"]:  # Avoid duplicates
                        row[key] = value
                
                excel_data.append(row)
            
            if not excel_data:
                logger.warning("No data to save to Excel")
                return
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Save to Excel
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(output_path, index=False, engine='openpyxl')
            logger.info(f"Saved {len(excel_data)} stocks with factors to {output_path.absolute()}")
            
        except ImportError:
            logger.error("pandas and openpyxl required for Excel export. Install with: pip install pandas openpyxl")
        except Exception as e:
            logger.error(f"Failed to save factors to Excel: {e}")
            raise

