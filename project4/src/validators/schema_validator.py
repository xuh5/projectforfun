"""Schema validators for ensuring data structure."""

from typing import Dict, Any, List, Optional, Set, Type, get_args, get_origin
import logging

from ..core import Validator, ValidationResult


logger = logging.getLogger(__name__)


class SchemaValidator(Validator):
    """
    Validates record against a schema definition.
    
    Config options:
        - schema: Dict[str, Any] - schema definition
          Format: {
              'field_name': {
                  'type': type or str,  # Required: expected type
                  'required': bool,      # Optional: whether field is required
                  'nullable': bool,      # Optional: whether field can be None
              }
          }
    """
    
    TYPE_MAP = {
        'str': str,
        'string': str,
        'int': int,
        'integer': int,
        'float': float,
        'number': float,
        'bool': bool,
        'boolean': bool,
        'dict': dict,
        'list': list,
        'array': list,
    }
    
    def __init__(self, schema: Optional[Dict[str, Dict[str, Any]]] = None, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize schema validator.
        
        Args:
            schema: Schema definition
            config: Additional configuration
        """
        super().__init__(config)
        self.schema = schema or self.config.get('schema', {})
        self._normalize_schema()
    
    def _normalize_schema(self):
        """Normalize schema types to Python types."""
        for field_name, field_def in self.schema.items():
            if isinstance(field_def.get('type'), str):
                type_str = field_def['type'].lower()
                if type_str in self.TYPE_MAP:
                    field_def['type'] = self.TYPE_MAP[type_str]
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate record against schema."""
        errors = []
        warnings = []
        
        # Check required fields
        for field_name, field_def in self.schema.items():
            required = field_def.get('required', False)
            nullable = field_def.get('nullable', True)
            expected_type = field_def.get('type')
            
            # Check if field exists
            if field_name not in record:
                if required:
                    errors.append(f"Required field '{field_name}' is missing")
                continue
            
            value = record[field_name]
            
            # Check nullability
            if value is None:
                if not nullable and required:
                    errors.append(f"Field '{field_name}' cannot be None")
                continue
            
            # Check type
            if expected_type and not self._check_type(value, expected_type):
                errors.append(
                    f"Field '{field_name}' has wrong type. "
                    f"Expected: {self._type_name(expected_type)}, "
                    f"got: {type(value).__name__}"
                )
        
        # Check for unexpected fields
        schema_fields = set(self.schema.keys())
        record_fields = set(record.keys())
        unexpected_fields = record_fields - schema_fields
        
        if unexpected_fields:
            warnings.append(
                f"Unexpected fields found: {', '.join(unexpected_fields)}"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors,
            warnings=warnings
        )
    
    def _check_type(self, value: Any, expected_type: Type) -> bool:
        """Check if value matches expected type."""
        try:
            return isinstance(value, expected_type)
        except TypeError:
            # Handle complex types
            return type(value).__name__ == str(expected_type)
    
    def _type_name(self, t: Type) -> str:
        """Get readable type name."""
        if hasattr(t, '__name__'):
            return t.__name__
        return str(t)

