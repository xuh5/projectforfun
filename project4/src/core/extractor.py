"""Extractor interface for data extraction."""

from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional


class Extractor(ABC):
    """
    Abstract base class for data extractors.
    
    Extractors are responsible for reading data from various sources
    (files, APIs, databases) and yielding records one at a time.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extractor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def extract(self) -> Iterator[Dict[str, Any]]:
        """
        Extract data from the source.
        
        Yields:
            Dictionary records from the data source
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

