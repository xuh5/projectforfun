"""Filter for selecting relevant stocks based on criteria."""

import logging
from typing import Dict, List, Optional, Set
from factors.registry import FactorRegistry
from factors.manager import FactorManager

logger = logging.getLogger(__name__)


class Filter:
    """Filters stocks based on specified criteria."""
    
    def __init__(self, factor_manager: Optional[FactorManager] = None, factor_registry: Optional[FactorRegistry] = None):
        """
        Initialize filter.
        
        Args:
            factor_manager: FactorManager instance to get available factors
            factor_registry: FactorRegistry instance (alternative to manager)
        """
        self.factor_manager = factor_manager
        self.factor_registry = factor_registry or (factor_manager.registry if factor_manager else None)
        self._available_factors: Optional[Set[str]] = None
    
    def get_available_factors(self) -> Set[str]:
        """
        Get set of available factors dynamically.
        
        Returns:
            Set of available factor names
        """
        if self._available_factors is not None:
            return self._available_factors
        
        if self.factor_manager:
            self._available_factors = self.factor_manager.get_available_factors()
        elif self.factor_registry:
            self._available_factors = self.factor_registry.get_all_factors()
        else:
            self._available_factors = set()
            logger.warning("No factor manager or registry provided. Available factors will be empty.")
        
        # Don't log here - keep it quiet
        
        return self._available_factors
    
    def filter(self, stocks: List[Dict]) -> List[str]:
        """
        Filter stocks based on criteria.
        
        Can use available factors dynamically to filter stocks.
        
        Args:
            stocks: List of stock data dictionaries with keys:
                - symbol: Stock ticker
                - name: Company name
                - sector: Industry sector
                - industry: Specific industry
                - marketCap: Market capitalization
                - exchange: Stock exchange
                - Any other factors from registered providers
        
        Returns:
            List of stock symbols that pass the filter
        """
        # Get available factors for reference
        available_factors = self.get_available_factors()
        
        if available_factors:
            logger.debug(f"Filtering with {len(available_factors)} available factors")
        
        filtered_symbols = []
        
        for stock in stocks:
            symbol = stock.get("symbol")
            name = stock.get("name")
            sector = stock.get("sector")
            
            # Basic validation: must have symbol and name
            if not symbol or not name:
                logger.debug(f"Skipping stock with missing symbol or name: {stock}")
                continue
            
            # Filter by marketCap > 5M (5,000,000)
            if 'marketCap' in available_factors:
                market_cap = stock.get("marketCap")
                if market_cap is None:
                    logger.debug(f"Skipping {symbol}: marketCap is missing")
                    continue
                # marketCap is in USD, 5M = 5,000,000
                if market_cap <= 5_000_000:
                    logger.debug(f"Skipping {symbol}: marketCap {market_cap} <= 5M")
                    continue
            
            filtered_symbols.append(symbol)
            logger.debug(f"Accepted: {symbol} - {name} (marketCap: {stock.get('marketCap')})")
        
        # Don't log here - keep it quiet
        return filtered_symbols

