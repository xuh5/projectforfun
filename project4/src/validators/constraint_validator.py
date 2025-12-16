"""Constraint validators for business rules."""

from typing import Dict, Any, List, Optional, Callable, Union
import re

from ..core import Validator, ValidationResult


class Constraint:
    """Base class for constraints."""
    
    def check(self, value: Any) -> bool:
        """Check if value satisfies constraint."""
        raise NotImplementedError
    
    def message(self, field_name: str, value: Any) -> str:
        """Get error message for failed constraint."""
        raise NotImplementedError


class RangeConstraint(Constraint):
    """Constraint for numeric ranges."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None):
        self.min_value = min_value
        self.max_value = max_value
    
    def check(self, value: Any) -> bool:
        """Check if value is in range."""
        try:
            num = float(value)
            if self.min_value is not None and num < self.min_value:
                return False
            if self.max_value is not None and num > self.max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def message(self, field_name: str, value: Any) -> str:
        """Get error message."""
        if self.min_value is not None and self.max_value is not None:
            return f"Field '{field_name}' must be between {self.min_value} and {self.max_value}, got {value}"
        elif self.min_value is not None:
            return f"Field '{field_name}' must be >= {self.min_value}, got {value}"
        else:
            return f"Field '{field_name}' must be <= {self.max_value}, got {value}"


class LengthConstraint(Constraint):
    """Constraint for string/list length."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def check(self, value: Any) -> bool:
        """Check if length is valid."""
        try:
            length = len(value)
            if self.min_length is not None and length < self.min_length:
                return False
            if self.max_length is not None and length > self.max_length:
                return False
            return True
        except TypeError:
            return False
    
    def message(self, field_name: str, value: Any) -> str:
        """Get error message."""
        length = len(value) if hasattr(value, '__len__') else 'N/A'
        if self.min_length is not None and self.max_length is not None:
            return f"Field '{field_name}' length must be between {self.min_length} and {self.max_length}, got {length}"
        elif self.min_length is not None:
            return f"Field '{field_name}' length must be >= {self.min_length}, got {length}"
        else:
            return f"Field '{field_name}' length must be <= {self.max_length}, got {length}"


class RegexConstraint(Constraint):
    """Constraint for regex pattern matching."""
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.regex = re.compile(pattern)
    
    def check(self, value: Any) -> bool:
        """Check if value matches pattern."""
        return bool(self.regex.match(str(value)))
    
    def message(self, field_name: str, value: Any) -> str:
        """Get error message."""
        return f"Field '{field_name}' does not match pattern '{self.pattern}', got '{value}'"


class EnumConstraint(Constraint):
    """Constraint for enum/allowed values."""
    
    def __init__(self, allowed_values: List[Any]):
        self.allowed_values = set(allowed_values)
    
    def check(self, value: Any) -> bool:
        """Check if value is in allowed values."""
        return value in self.allowed_values
    
    def message(self, field_name: str, value: Any) -> str:
        """Get error message."""
        return f"Field '{field_name}' must be one of {self.allowed_values}, got '{value}'"


class ConstraintValidator(Validator):
    """
    Validates constraints on fields.
    
    Config options:
        - constraints: Dict[str, List[Constraint]] - field to constraints mapping
    """
    
    def __init__(
        self,
        constraints: Optional[Dict[str, List[Constraint]]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize constraint validator.
        
        Args:
            constraints: Mapping of field names to constraint lists
            config: Additional configuration
        """
        super().__init__(config)
        self.constraints = constraints or self.config.get('constraints', {})
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate constraints in record."""
        errors = []
        
        for field_name, constraint_list in self.constraints.items():
            if field_name not in record:
                continue
            
            value = record[field_name]
            if value is None:
                continue
            
            for constraint in constraint_list:
                if not constraint.check(value):
                    errors.append(constraint.message(field_name, value))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )


class RequiredFieldValidator(Validator):
    """
    Validates required fields.
    
    Config options:
        - required_fields: List[str] - list of required field names
    """
    
    def __init__(
        self,
        required_fields: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize required field validator.
        
        Args:
            required_fields: List of required field names
            config: Additional configuration
        """
        super().__init__(config)
        self.required_fields = required_fields or self.config.get('required_fields', [])
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate required fields."""
        errors = []
        
        for field_name in self.required_fields:
            if field_name not in record:
                errors.append(f"Required field '{field_name}' is missing")
            elif record[field_name] is None:
                errors.append(f"Required field '{field_name}' cannot be None")
            elif isinstance(record[field_name], str) and not record[field_name].strip():
                errors.append(f"Required field '{field_name}' cannot be empty")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )

