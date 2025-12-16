"""Format validators for common data types."""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import re

from ..core import Validator, ValidationResult


class FormatValidator(Validator):
    """
    Validates field formats.
    
    Config options:
        - fields: Dict[str, str] - field name to format type mapping
          Supported types: 'date', 'datetime', 'number', 'integer', 'float', 
                          'email', 'phone', 'url'
    """
    
    FORMAT_VALIDATORS = {
        'email': lambda v: bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(v))),
        'phone': lambda v: bool(re.match(r'^\+?1?\d{9,15}$', str(v).replace('-', '').replace(' ', ''))),
        'url': lambda v: bool(re.match(r'^https?://[^\s]+$', str(v))),
    }
    
    def __init__(self, fields: Optional[Dict[str, str]] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize format validator.
        
        Args:
            fields: Field name to format type mapping
            config: Additional configuration
        """
        super().__init__(config)
        self.fields = fields or self.config.get('fields', {})
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate field formats in record."""
        errors = []
        
        for field_name, format_type in self.fields.items():
            if field_name not in record:
                continue
            
            value = record[field_name]
            if value is None:
                continue
            
            try:
                if not self._validate_format(value, format_type):
                    errors.append(f"Field '{field_name}' has invalid format. Expected: {format_type}")
            except Exception as e:
                errors.append(f"Field '{field_name}' format validation error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )
    
    def _validate_format(self, value: Any, format_type: str) -> bool:
        """Validate a value against a format type."""
        if format_type == 'number' or format_type == 'integer' or format_type == 'float':
            try:
                float(value)
                if format_type == 'integer':
                    return float(value).is_integer()
                return True
            except (ValueError, TypeError):
                return False
        
        if format_type in self.FORMAT_VALIDATORS:
            return self.FORMAT_VALIDATORS[format_type](value)
        
        return True


class DateFormatValidator(Validator):
    """
    Validates date/datetime formats.
    
    Config options:
        - fields: List[str] - field names to validate
        - format: str - date format string (default: ISO format)
    """
    
    def __init__(
        self, 
        fields: Optional[List[str]] = None,
        date_format: str = "%Y-%m-%d",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize date format validator.
        
        Args:
            fields: List of field names to validate
            date_format: Expected date format string
            config: Additional configuration
        """
        super().__init__(config)
        self.fields = fields or self.config.get('fields', [])
        self.date_format = date_format
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate date formats in record."""
        errors = []
        
        for field_name in self.fields:
            if field_name not in record:
                continue
            
            value = record[field_name]
            if value is None:
                continue
            
            try:
                # Try to parse as date
                if isinstance(value, str):
                    datetime.strptime(value, self.date_format)
                elif not isinstance(value, datetime):
                    errors.append(
                        f"Field '{field_name}' must be a string or datetime object"
                    )
            except ValueError as e:
                errors.append(
                    f"Field '{field_name}' has invalid date format. "
                    f"Expected: {self.date_format}, got: {value}"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )


class NumberFormatValidator(Validator):
    """
    Validates numeric formats.
    
    Config options:
        - fields: List[str] - field names to validate
        - allow_float: bool - whether to allow float values
    """
    
    def __init__(
        self,
        fields: Optional[List[str]] = None,
        allow_float: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize number format validator.
        
        Args:
            fields: List of field names to validate
            allow_float: Whether to allow float values
            config: Additional configuration
        """
        super().__init__(config)
        self.fields = fields or self.config.get('fields', [])
        self.allow_float = allow_float
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate number formats in record."""
        errors = []
        
        for field_name in self.fields:
            if field_name not in record:
                continue
            
            value = record[field_name]
            if value is None:
                continue
            
            try:
                num = float(value)
                if not self.allow_float and not num.is_integer():
                    errors.append(
                        f"Field '{field_name}' must be an integer, got float: {value}"
                    )
            except (ValueError, TypeError):
                errors.append(
                    f"Field '{field_name}' must be a number, got: {type(value).__name__}"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )

