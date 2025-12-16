"""Duplicate detection validator."""

from typing import Dict, Any, List, Optional, Set, Tuple
import hashlib
import json

from ..core import Validator, ValidationResult


class DuplicateValidator(Validator):
    """
    Detects duplicate records based on key fields.
    
    Config options:
        - key_fields: List[str] - fields to use for duplicate detection
        - case_sensitive: bool - whether comparison is case-sensitive (default: True)
    """
    
    def __init__(
        self,
        key_fields: Optional[List[str]] = None,
        case_sensitive: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize duplicate validator.
        
        Args:
            key_fields: Fields to use for duplicate detection
            case_sensitive: Whether comparison is case-sensitive
            config: Additional configuration
        """
        super().__init__(config)
        self.key_fields = key_fields or self.config.get('key_fields', [])
        self.case_sensitive = case_sensitive
        self._seen_keys: Set[str] = set()
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Check if record is a duplicate."""
        errors = []
        
        # Generate key from key fields
        key = self._generate_key(record)
        
        if key in self._seen_keys:
            key_values = {k: record.get(k) for k in self.key_fields if k in record}
            errors.append(
                f"Duplicate record detected. Key fields: {key_values}"
            )
        else:
            self._seen_keys.add(key)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors,
            metadata={'duplicate_key': key}
        )
    
    def _generate_key(self, record: Dict[str, Any]) -> str:
        """Generate a unique key for the record based on key fields."""
        key_parts = []
        
        for field in self.key_fields:
            value = record.get(field, '')
            
            # Normalize value
            if isinstance(value, str):
                if not self.case_sensitive:
                    value = value.lower()
                value = value.strip()
            
            key_parts.append(str(value))
        
        # Create hash of key parts
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def reset(self):
        """Reset the seen keys (useful for new batches)."""
        self._seen_keys.clear()
    
    def get_duplicate_count(self) -> int:
        """Get count of unique records seen."""
        return len(self._seen_keys)


class CrossBatchDuplicateValidator(Validator):
    """
    Detects duplicates across multiple batches using persistent storage.
    
    This version keeps track of seen records across different pipeline runs.
    """
    
    def __init__(
        self,
        key_fields: Optional[List[str]] = None,
        storage_path: Optional[str] = None,
        case_sensitive: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize cross-batch duplicate validator.
        
        Args:
            key_fields: Fields to use for duplicate detection
            storage_path: Path to store seen keys (if None, uses memory only)
            case_sensitive: Whether comparison is case-sensitive
            config: Additional configuration
        """
        super().__init__(config)
        self.key_fields = key_fields or self.config.get('key_fields', [])
        self.storage_path = storage_path
        self.case_sensitive = case_sensitive
        self._seen_keys: Set[str] = set()
        
        # Load existing keys if storage path provided
        if self.storage_path:
            self._load_seen_keys()
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Check if record is a duplicate."""
        errors = []
        
        # Generate key from key fields
        key_parts = []
        for field in self.key_fields:
            value = record.get(field, '')
            if isinstance(value, str) and not self.case_sensitive:
                value = value.lower()
            key_parts.append(str(value))
        
        key = '|'.join(key_parts)
        
        if key in self._seen_keys:
            errors.append(f"Duplicate record detected based on key fields: {self.key_fields}")
        else:
            self._seen_keys.add(key)
            if self.storage_path:
                self._save_key(key)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )
    
    def _load_seen_keys(self):
        """Load seen keys from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                self._seen_keys = set(line.strip() for line in f)
        except FileNotFoundError:
            pass
    
    def _save_key(self, key: str):
        """Save a new key to storage."""
        try:
            with open(self.storage_path, 'a') as f:
                f.write(f"{key}\n")
        except Exception as e:
            # Log error but don't fail validation
            pass

