"""Validator interface for data validation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    """Whether the record passed validation."""
    
    record: Dict[str, Any]
    """The validated record."""
    
    errors: List[str] = field(default_factory=list)
    """List of validation error messages."""
    
    warnings: List[str] = field(default_factory=list)
    """List of validation warnings (non-blocking)."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the validation."""


class Validator(ABC):
    """
    Abstract base class for validators.
    
    Validators check data quality and can be chained together
    to form validation pipelines.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single record.
        
        Args:
            record: The record to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        pass
    
    def __call__(self, record: Dict[str, Any]) -> ValidationResult:
        """Allow validator to be called directly."""
        return self.validate(record)


class ValidatorChain:
    """
    Chain multiple validators together.
    
    Validators are executed in order. If any validator fails,
    the chain stops and returns the failed result.
    """
    
    def __init__(self, validators: List[Validator], stop_on_first_error: bool = True):
        """
        Initialize validator chain.
        
        Args:
            validators: List of validators to chain
            stop_on_first_error: Whether to stop validation on first error
        """
        self.validators = validators
        self.stop_on_first_error = stop_on_first_error
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """
        Validate record through all validators in chain.
        
        Args:
            record: The record to validate
            
        Returns:
            Combined ValidationResult from all validators
        """
        all_errors = []
        all_warnings = []
        combined_metadata = {}
        
        for validator in self.validators:
            result = validator.validate(record)
            
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            combined_metadata.update(result.metadata)
            
            if not result.is_valid and self.stop_on_first_error:
                return ValidationResult(
                    is_valid=False,
                    record=record,
                    errors=all_errors,
                    warnings=all_warnings,
                    metadata=combined_metadata
                )
        
        is_valid = len(all_errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            record=record,
            errors=all_errors,
            warnings=all_warnings,
            metadata=combined_metadata
        )

