"""Data transformation and cleaning utilities."""

from typing import Dict, Any, Optional, Callable, List
import re
import logging

from ..core import Transformer


logger = logging.getLogger(__name__)


class DataCleaner(Transformer):
    """
    General-purpose data cleaner.
    
    Config options:
        - strip_whitespace: bool - strip whitespace from strings (default: True)
        - remove_empty_strings: bool - convert empty strings to None (default: True)
        - lowercase_keys: bool - convert all keys to lowercase (default: False)
        - remove_metadata_fields: bool - remove fields starting with '_' (default: False)
    """
    
    def __init__(
        self,
        strip_whitespace: bool = True,
        remove_empty_strings: bool = True,
        lowercase_keys: bool = False,
        remove_metadata_fields: bool = False,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize data cleaner.
        
        Args:
            strip_whitespace: Whether to strip whitespace
            remove_empty_strings: Whether to convert empty strings to None
            lowercase_keys: Whether to lowercase all keys
            remove_metadata_fields: Whether to remove metadata fields
            config: Additional configuration
        """
        super().__init__(config)
        self.strip_whitespace = strip_whitespace
        self.remove_empty_strings = remove_empty_strings
        self.lowercase_keys = lowercase_keys
        self.remove_metadata_fields = remove_metadata_fields
    
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the record."""
        result = {}
        
        for key, value in record.items():
            # Skip metadata fields if configured
            if self.remove_metadata_fields and key.startswith('_'):
                continue
            
            # Transform key
            new_key = key.lower() if self.lowercase_keys else key
            
            # Transform value
            new_value = self._clean_value(value)
            
            result[new_key] = new_value
        
        return result
    
    def _clean_value(self, value: Any) -> Any:
        """Clean a single value."""
        if isinstance(value, str):
            if self.strip_whitespace:
                value = value.strip()
            
            if self.remove_empty_strings and value == '':
                return None
        
        elif isinstance(value, dict):
            # Recursively clean nested dicts
            return self.transform(value)
        
        elif isinstance(value, list):
            # Clean list items
            return [self._clean_value(item) for item in value]
        
        return value


class FieldMapper(Transformer):
    """
    Maps field names to new names.
    
    Config options:
        - field_map: Dict[str, str] - mapping of old field names to new names
        - remove_unmapped: bool - remove fields not in mapping (default: False)
    """
    
    def __init__(
        self,
        field_map: Optional[Dict[str, str]] = None,
        remove_unmapped: bool = False,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize field mapper.
        
        Args:
            field_map: Mapping of old to new field names
            remove_unmapped: Whether to remove unmapped fields
            config: Additional configuration
        """
        super().__init__(config)
        self.field_map = field_map or self.config.get('field_map', {})
        self.remove_unmapped = remove_unmapped
    
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Map field names."""
        result = {}
        
        for key, value in record.items():
            if key in self.field_map:
                new_key = self.field_map[key]
                result[new_key] = value
            elif not self.remove_unmapped:
                result[key] = value
        
        return result


class DefaultValueFiller(Transformer):
    """
    Fills missing or None values with defaults.
    
    Config options:
        - defaults: Dict[str, Any] - field to default value mapping
        - fill_empty_strings: bool - treat empty strings as missing (default: True)
    """
    
    def __init__(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        fill_empty_strings: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize default value filler.
        
        Args:
            defaults: Mapping of field names to default values
            fill_empty_strings: Whether to treat empty strings as missing
            config: Additional configuration
        """
        super().__init__(config)
        self.defaults = defaults or self.config.get('defaults', {})
        self.fill_empty_strings = fill_empty_strings
    
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing values with defaults."""
        result = record.copy()
        
        for field, default_value in self.defaults.items():
            if field not in result or result[field] is None:
                result[field] = default_value
            elif self.fill_empty_strings and isinstance(result[field], str) and result[field] == '':
                result[field] = default_value
        
        return result


class TypeConverter(Transformer):
    """
    Converts field types.
    
    Config options:
        - conversions: Dict[str, Callable] - field to conversion function mapping
    """
    
    def __init__(
        self,
        conversions: Optional[Dict[str, Callable]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize type converter.
        
        Args:
            conversions: Mapping of field names to conversion functions
            config: Additional configuration
        """
        super().__init__(config)
        self.conversions = conversions or self.config.get('conversions', {})
    
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert field types."""
        result = record.copy()
        
        for field, converter in self.conversions.items():
            if field in result and result[field] is not None:
                try:
                    result[field] = converter(result[field])
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert field '{field}': {e}")
        
        return result


class FieldRemover(Transformer):
    """
    Removes specified fields from records.
    
    Config options:
        - fields: List[str] - fields to remove
        - pattern: str - regex pattern for fields to remove
    """
    
    def __init__(
        self,
        fields: Optional[List[str]] = None,
        pattern: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize field remover.
        
        Args:
            fields: List of field names to remove
            pattern: Regex pattern for field names to remove
            config: Additional configuration
        """
        super().__init__(config)
        self.fields = set(fields or self.config.get('fields', []))
        self.pattern = re.compile(pattern) if pattern else None
    
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Remove specified fields."""
        result = {}
        
        for key, value in record.items():
            should_remove = (
                key in self.fields or
                (self.pattern and self.pattern.match(key))
            )
            
            if not should_remove:
                result[key] = value
        
        return result

