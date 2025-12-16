"""Transformer interface for data transformation."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Transformer(ABC):
    """
    Abstract base class for data transformers.
    
    Transformers modify, clean, or enrich data records.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the transformer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single record.
        
        Args:
            record: The record to transform
            
        Returns:
            Transformed record
        """
        pass
    
    def __call__(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Allow transformer to be called directly."""
        return self.transform(record)


class TransformerChain:
    """Chain multiple transformers together."""
    
    def __init__(self, transformers: list[Transformer]):
        """
        Initialize transformer chain.
        
        Args:
            transformers: List of transformers to chain
        """
        self.transformers = transformers
    
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform record through all transformers in chain.
        
        Args:
            record: The record to transform
            
        Returns:
            Transformed record
        """
        result = record
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result

