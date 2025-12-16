"""Buffer interface for error data quarantine and retry management."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class QuarantinedRecord:
    """A record that has been quarantined due to validation errors."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique identifier for this quarantined record."""
    
    record: Dict[str, Any] = field(default_factory=dict)
    """The actual data record."""
    
    errors: List[str] = field(default_factory=list)
    """List of validation errors."""
    
    quarantined_at: datetime = field(default_factory=datetime.utcnow)
    """When the record was quarantined."""
    
    retry_count: int = 0
    """Number of times this record has been retried."""
    
    last_retry_at: Optional[datetime] = None
    """When the last retry occurred."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "record": self.record,
            "errors": self.errors,
            "quarantined_at": self.quarantined_at.isoformat(),
            "retry_count": self.retry_count,
            "last_retry_at": self.last_retry_at.isoformat() if self.last_retry_at else None,
            "metadata": self.metadata,
        }


class Buffer(ABC):
    """
    Abstract base class for error data buffer/quarantine.
    
    Buffers store failed records for later inspection and retry.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the buffer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def quarantine(self, record: Dict[str, Any], errors: List[str], 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Quarantine a record with errors.
        
        Args:
            record: The failed record
            errors: List of error messages
            metadata: Optional additional metadata
            
        Returns:
            Quarantine ID
        """
        pass
    
    @abstractmethod
    def get_quarantined(self, limit: Optional[int] = None) -> List[QuarantinedRecord]:
        """
        Get quarantined records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of quarantined records
        """
        pass
    
    @abstractmethod
    def get_by_id(self, quarantine_id: str) -> Optional[QuarantinedRecord]:
        """
        Get a specific quarantined record by ID.
        
        Args:
            quarantine_id: The quarantine ID
            
        Returns:
            QuarantinedRecord if found, None otherwise
        """
        pass
    
    @abstractmethod
    def release(self, quarantine_id: str) -> bool:
        """
        Release a quarantined record.
        
        Args:
            quarantine_id: The quarantine ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update_retry(self, quarantine_id: str) -> bool:
        """
        Update retry count for a quarantined record.
        
        Args:
            quarantine_id: The quarantine ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Get total count of quarantined records.
        
        Returns:
            Number of quarantined records
        """
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """
        Clear all quarantined records.
        
        Returns:
            Number of records cleared
        """
        pass

