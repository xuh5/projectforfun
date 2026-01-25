"""Base classes for factor providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


class FactorProvider(ABC):
    """Base class for all factor providers."""
    
    def __init__(self, name: str):
        """
        Initialize factor provider.
        
        Args:
            name: Unique name for this provider
        """
        self.name = name
        self._available_factors: Set[str] = set()
    
    @abstractmethod
    def fetch_factors(self, symbols: List[str], **kwargs) -> Dict[str, Dict]:
        """
        Fetch factors for given symbols.
        
        Args:
            symbols: List of stock symbols
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary mapping symbol to factor data dict
        """
        pass
    
    @abstractmethod
    def get_available_factors(self) -> Set[str]:
        """
        Get set of factor names this provider can supply.
        
        Returns:
            Set of factor names (e.g., {'marketCap', 'peRatio', 'dividendYield'})
        """
        pass
    
    def extract_factors(self, data: Dict, factor_names: Set[str]) -> Dict:
        """
        Extract specific factors from provider data.
        Only extracts factors that exist in data, warns about missing ones.
        
        Args:
            data: Raw data from provider (single symbol's data)
            factor_names: Set of factor names to extract
            
        Returns:
            Dictionary with only requested factors that exist
        """
        # Get factors that actually exist in the data
        available_in_data = set(data.keys())
        requested = factor_names & available_in_data
        
        # Warn about missing factors
        missing = factor_names - available_in_data
        if missing:
            logger.warning(
                f"Provider {self.name}: Missing factors {missing} (available: {len(available_in_data)} factors)"
            )
        
        return {k: v for k, v in data.items() if k in requested}

