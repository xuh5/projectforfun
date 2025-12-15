"""Validator for generated JSON data against schema."""

import json
import re
from typing import Any, Dict, List, Optional, Tuple


class SchemaValidator:
    """Validate generated JSON data against schema definition."""
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize validator with schema.
        
        Args:
            schema: Schema dictionary from SchemaParser
        """
        self.schema = schema
        self.fields = schema.get("fields", {})
        self.errors: List[str] = []
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against schema.
        
        Args:
            data: Generated JSON data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []
        
        # Check required fields
        self._check_required_fields(data)
        
        # Validate each field
        for field_name, field_info in self.fields.items():
            if field_name in data:
                self._validate_field(field_name, data[field_name], field_info)
        
        return len(self.errors) == 0, self.errors
    
    def _check_required_fields(self, data: Dict[str, Any]) -> None:
        """Check that all required fields are present."""
        for field_name, field_info in self.fields.items():
            if isinstance(field_info, dict) and field_info.get("required", False):
                if field_name not in data:
                    self.errors.append(f"Missing required field: {field_name}")
    
    def _validate_field(self, field_name: str, value: Any, field_info: Dict[str, Any]) -> None:
        """Validate a single field."""
        field_type = field_info.get("type", "string")
        
        # Type validation
        if not self._check_type(value, field_type):
            self.errors.append(
                f"Field '{field_name}': expected {field_type}, got {type(value).__name__}"
            )
            return
        
        # Format validation
        if "format" in field_info:
            if not self._check_format(value, field_info["format"]):
                self.errors.append(
                    f"Field '{field_name}': invalid format '{field_info['format']}'"
                )
        
        # String constraints
        if field_type == "string" and isinstance(value, str):
            if "minLength" in field_info and len(value) < field_info["minLength"]:
                self.errors.append(
                    f"Field '{field_name}': length {len(value)} < minLength {field_info['minLength']}"
                )
            if "maxLength" in field_info and len(value) > field_info["maxLength"]:
                self.errors.append(
                    f"Field '{field_name}': length {len(value)} > maxLength {field_info['maxLength']}"
                )
            if "pattern" in field_info:
                if not re.match(field_info["pattern"], value):
                    self.errors.append(
                        f"Field '{field_name}': does not match pattern '{field_info['pattern']}'"
                    )
            if "enum" in field_info:
                if value not in field_info["enum"]:
                    self.errors.append(
                        f"Field '{field_name}': value '{value}' not in enum {field_info['enum']}"
                    )
        
        # Number constraints
        if field_type in ["integer", "number"]:
            if "min" in field_info and value < field_info["min"]:
                self.errors.append(
                    f"Field '{field_name}': value {value} < min {field_info['min']}"
                )
            if "max" in field_info and value > field_info["max"]:
                self.errors.append(
                    f"Field '{field_name}': value {value} > max {field_info['max']}"
                )
        
        # Object validation
        if field_type == "object" and isinstance(value, dict):
            if "fields" in field_info:
                nested_validator = SchemaValidator({"fields": field_info["fields"]})
                is_valid, nested_errors = nested_validator.validate(value)
                if not is_valid:
                    self.errors.extend([f"{field_name}.{err}" for err in nested_errors])
        
        # Array validation
        if field_type == "array" and isinstance(value, list):
            if "minItems" in field_info and len(value) < field_info["minItems"]:
                self.errors.append(
                    f"Field '{field_name}': array length {len(value)} < minItems {field_info['minItems']}"
                )
            if "maxItems" in field_info and len(value) > field_info["maxItems"]:
                self.errors.append(
                    f"Field '{field_name}': array length {len(value)} > maxItems {field_info['maxItems']}"
                )
            if "items" in field_info:
                items_info = field_info["items"]
                for i, item in enumerate(value):
                    self._validate_field(f"{field_name}[{i}]", item, items_info)
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation
        
        if isinstance(expected_python_type, tuple):
            return isinstance(value, expected_python_type)
        return isinstance(value, expected_python_type)
    
    def _check_format(self, value: Any, format_type: str) -> bool:
        """Check if value matches format."""
        if not isinstance(value, str):
            return False
        
        format_patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "url": r"^https?://.+",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "datetime": r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",
        }
        
        pattern = format_patterns.get(format_type)
        if pattern:
            return bool(re.match(pattern, value, re.IGNORECASE))
        
        return True  # Unknown format, skip validation

