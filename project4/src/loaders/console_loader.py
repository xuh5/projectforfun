"""Console loader for debugging and testing."""

import json
from typing import Dict, Any, Optional
import logging

from ..core import Loader


logger = logging.getLogger(__name__)


class ConsoleLoader(Loader):
    """
    Loads data to console (prints records).
    
    Useful for debugging and testing pipelines.
    
    Config options:
        - format: str - output format: 'json', 'pretty', or 'simple' (default: 'pretty')
        - max_length: int - maximum length to print (default: None = unlimited)
    """
    
    def __init__(
        self,
        format: str = 'pretty',
        max_length: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize console loader.
        
        Args:
            format: Output format ('json', 'pretty', 'simple')
            max_length: Maximum length to print
            config: Additional configuration
        """
        super().__init__(config)
        self.format = format
        self.max_length = max_length
        self._count = 0
    
    def load(self, record: Dict[str, Any]) -> bool:
        """Print record to console."""
        self._count += 1
        
        try:
            if self.format == 'json':
                output = json.dumps(record, ensure_ascii=False)
            elif self.format == 'pretty':
                output = json.dumps(record, indent=2, ensure_ascii=False)
            else:  # simple
                output = str(record)
            
            # Truncate if needed
            if self.max_length and len(output) > self.max_length:
                output = output[:self.max_length] + '...'
            
            print(f"[Record {self._count}] {output}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to print record: {e}")
            return False

