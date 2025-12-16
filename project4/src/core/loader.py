"""Loader interface for loading data to destinations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class Loader(ABC):
    """
    Abstract base class for data loaders.
    
    Loaders write data to various destinations
    (files, databases, APIs).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the loader.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def load(self, record: Dict[str, Any]) -> bool:
        """
        Load a single record to the destination.
        
        Args:
            record: The record to load
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def load_batch(self, records: List[Dict[str, Any]]) -> int:
        """
        Load multiple records (default implementation).
        
        Args:
            records: List of records to load
            
        Returns:
            Number of successfully loaded records
        """
        success_count = 0
        for record in records:
            if self.load(record):
                success_count += 1
        return success_count
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

