"""Fetch stock factors using yfinance."""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
import yfinance as yf

from ..base import FactorProvider

logger = logging.getLogger(__name__)


class YFinanceFactorFetcher(FactorProvider):
    """Fetches stock factors using yfinance and saves to factors directory."""
    
    def __init__(self, factors_dir: str = "factors", delay: float = 1.5):
        """
        Initialize yfinance factor fetcher.
        
        Args:
            factors_dir: Directory to save factor data (default: "factors")
            delay: Delay between API requests in seconds (default: 1.5)
        """
        super().__init__(name="yfinance")
        self.factors_dir = Path(factors_dir)
        self.factors_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self._discovery_attempted = False  # Track if discovery has been attempted
    
    def fetch_factors(self, symbols: List[str], delay: Optional[float] = None) -> Dict[str, Dict]:
        """
        Fetch yfinance factors for a list of symbols.
        
        Args:
            symbols: List of stock symbols to fetch
            delay: Delay between requests in seconds (uses self.delay if not provided)
            
        Returns:
            Dictionary mapping symbol to factor data
        """
        # Use provided delay or fall back to instance delay
        request_delay = delay if delay is not None else self.delay
        
        logger.info(f"Fetching yfinance factors for {len(symbols)} symbols (delay: {request_delay}s)...")
        
        factors_data = {}
        failed_symbols = []
        
        for i, symbol in enumerate(symbols):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info:
                    logger.warning(f"No data returned for {symbol}")
                    failed_symbols.append(symbol)
                    continue
                
                info['ticker'] = symbol
                factors_data[symbol] = info
                
                # Update available factors from actual data
                if not self._available_factors:
                    self._available_factors = set(info.keys())
                else:
                    self._available_factors.update(info.keys())
                
                if i < len(symbols) - 1:
                    time.sleep(request_delay)
                    
            except Exception as e:
                logger.error(f"Failed to fetch factors for {symbol}: {e}")
                failed_symbols.append(symbol)
        
        logger.info(f"Fetched {len(factors_data)}/{len(symbols)} symbols")
        if failed_symbols:
            logger.warning(f"Failed: {failed_symbols}")
        
        return factors_data
    
    def get_available_factors(self) -> Set[str]:
        """
        Get set of factor names this provider can supply.
        Dynamically discovered from actual API calls.
        
        Returns:
            Set of factor names available from yfinance
        """
        # Only attempt discovery once to avoid repeated failed API calls
        if not self._discovery_attempted:
            self._discovery_attempted = True
            try:
                ticker = yf.Ticker("AAPL")
                info = ticker.info
                if info:
                    self._available_factors = set(info.keys())
                    logger.debug(f"Discovered {len(self._available_factors)} factors from sample")
                else:
                    logger.warning("No data returned during factor discovery")
            except Exception as e:
                logger.warning(f"Failed to discover factors: {e}")
                # Keep empty set but don't retry on next call
        
        return self._available_factors.copy()

