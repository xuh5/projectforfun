"""File-based buffer implementations."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import fcntl

from ..core import Buffer, QuarantinedRecord


logger = logging.getLogger(__name__)


class JSONFileBuffer(Buffer):
    """
    JSON file-based buffer for quarantined records.
    
    Persists quarantined records to a JSON file for durability.
    
    Config options:
        - file_path: str - path to quarantine file
        - auto_save: bool - whether to save after each operation (default: True)
    """
    
    def __init__(
        self,
        file_path: str,
        auto_save: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize JSON file buffer.
        
        Args:
            file_path: Path to quarantine file
            auto_save: Whether to save after each operation
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.auto_save = auto_save
        self._records: Dict[str, QuarantinedRecord] = {}
        
        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing records
        self._load()
        
        logger.info(f"Initialized JSONFileBuffer: {self.file_path}")
    
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
        
        if self.auto_save:
            self._save()
        
        logger.debug(f"Quarantined record {qr.id} to file: {len(errors)} errors")
        
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
            
            if self.auto_save:
                self._save()
            
            logger.debug(f"Released quarantined record {quarantine_id}")
            return True
        return False
    
    def update_retry(self, quarantine_id: str) -> bool:
        """Update retry count."""
        if quarantine_id in self._records:
            qr = self._records[quarantine_id]
            qr.retry_count += 1
            qr.last_retry_at = datetime.utcnow()
            
            if self.auto_save:
                self._save()
            
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
        
        if self.auto_save:
            self._save()
        
        logger.info(f"Cleared {count} quarantined records from file")
        return count
    
    def save(self):
        """Manually save records to file."""
        self._save()
    
    def reload(self):
        """Reload records from file."""
        self._load()
    
    def _save(self):
        """Save records to JSON file."""
        try:
            data = [qr.to_dict() for qr in self._records.values()]
            
            # Write with atomic rename
            temp_path = self.file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            temp_path.replace(self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to save quarantine file: {e}")
            raise
    
    def _load(self):
        """Load records from JSON file."""
        if not self.file_path.exists():
            logger.debug(f"Quarantine file does not exist yet: {self.file_path}")
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._records = {}
            for item in data:
                qr = QuarantinedRecord(
                    id=item['id'],
                    record=item['record'],
                    errors=item['errors'],
                    quarantined_at=datetime.fromisoformat(item['quarantined_at']),
                    retry_count=item.get('retry_count', 0),
                    last_retry_at=datetime.fromisoformat(item['last_retry_at']) if item.get('last_retry_at') else None,
                    metadata=item.get('metadata', {})
                )
                self._records[qr.id] = qr
            
            logger.info(f"Loaded {len(self._records)} quarantined records from file")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quarantine file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load quarantine file: {e}")
            raise


class FileBuffer(JSONFileBuffer):
    """Alias for JSONFileBuffer for backwards compatibility."""
    pass

