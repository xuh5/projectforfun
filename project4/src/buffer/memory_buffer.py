"""In-memory buffer implementation."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..core import Buffer, QuarantinedRecord


logger = logging.getLogger(__name__)


class MemoryBuffer(Buffer):
    """
    In-memory buffer for quarantined records.
    
    Suitable for development and testing. Data is lost when process ends.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize memory buffer."""
        super().__init__(config)
        self._records: Dict[str, QuarantinedRecord] = {}
        logger.info("Initialized MemoryBuffer")
    
    def quarantine(
        self,
        record: Dict[str, Any],
        errors: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Quarantine a record."""
        qr = QuarantinedRecord(
            record=record.copy(),
            errors=errors.copy(),
            metadata=metadata or {}
        )
        
        self._records[qr.id] = qr
        logger.debug(f"Quarantined record {qr.id}: {len(errors)} errors")
        
        return qr.id
    
    def get_quarantined(self, limit: Optional[int] = None) -> List[QuarantinedRecord]:
        """Get quarantined records."""
        records = list(self._records.values())
        
        if limit:
            records = records[:limit]
        
        return records
    
    def get_by_id(self, quarantine_id: str) -> Optional[QuarantinedRecord]:
        """Get a specific quarantined record."""
        return self._records.get(quarantine_id)
    
    def release(self, quarantine_id: str) -> bool:
        """Release a quarantined record."""
        if quarantine_id in self._records:
            del self._records[quarantine_id]
            logger.debug(f"Released quarantined record {quarantine_id}")
            return True
        return False
    
    def update_retry(self, quarantine_id: str) -> bool:
        """Update retry count."""
        if quarantine_id in self._records:
            qr = self._records[quarantine_id]
            qr.retry_count += 1
            qr.last_retry_at = datetime.utcnow()
            logger.debug(f"Updated retry count for {quarantine_id}: {qr.retry_count}")
            return True
        return False
    
    def count(self) -> int:
        """Get count of quarantined records."""
        return len(self._records)
    
    def clear(self) -> int:
        """Clear all quarantined records."""
        count = len(self._records)
        self._records.clear()
        logger.info(f"Cleared {count} quarantined records")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        if not self._records:
            return {
                "total_records": 0,
                "avg_errors_per_record": 0,
                "max_retry_count": 0,
            }
        
        error_counts = [len(qr.errors) for qr in self._records.values()]
        retry_counts = [qr.retry_count for qr in self._records.values()]
        
        return {
            "total_records": len(self._records),
            "avg_errors_per_record": sum(error_counts) / len(error_counts),
            "max_retry_count": max(retry_counts) if retry_counts else 0,
            "oldest_record": min(
                (qr.quarantined_at for qr in self._records.values()),
                default=None
            ),
        }

