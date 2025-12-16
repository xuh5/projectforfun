"""Tests for validators."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.validators import (
    FormatValidator,
    SchemaValidator,
    ConstraintValidator,
    RangeConstraint,
    RequiredFieldValidator,
    DuplicateValidator
)


def test_format_validator_valid_email():
    """Test format validator with valid email."""
    validator = FormatValidator(fields={'email': 'email'})
    result = validator.validate({'email': 'test@example.com'})
    
    assert result.is_valid
    assert len(result.errors) == 0


def test_format_validator_invalid_email():
    """Test format validator with invalid email."""
    validator = FormatValidator(fields={'email': 'email'})
    result = validator.validate({'email': 'not-an-email'})
    
    assert not result.is_valid
    assert len(result.errors) > 0


def test_schema_validator_valid():
    """Test schema validator with valid record."""
    validator = SchemaValidator(schema={
        'name': {'type': 'str', 'required': True},
        'age': {'type': 'int', 'required': False},
    })
    
    result = validator.validate({'name': 'John', 'age': 30})
    
    assert result.is_valid
    assert len(result.errors) == 0


def test_schema_validator_missing_required():
    """Test schema validator with missing required field."""
    validator = SchemaValidator(schema={
        'name': {'type': 'str', 'required': True},
    })
    
    result = validator.validate({'age': 30})
    
    assert not result.is_valid
    assert 'name' in str(result.errors[0])


def test_constraint_validator_range():
    """Test constraint validator with range."""
    validator = ConstraintValidator(constraints={
        'age': [RangeConstraint(min_value=0, max_value=120)]
    })
    
    # Valid
    result = validator.validate({'age': 30})
    assert result.is_valid
    
    # Invalid
    result = validator.validate({'age': 150})
    assert not result.is_valid


def test_required_field_validator():
    """Test required field validator."""
    validator = RequiredFieldValidator(required_fields=['name', 'email'])
    
    # Valid
    result = validator.validate({'name': 'John', 'email': 'john@example.com'})
    assert result.is_valid
    
    # Invalid - missing field
    result = validator.validate({'name': 'John'})
    assert not result.is_valid


def test_duplicate_validator():
    """Test duplicate validator."""
    validator = DuplicateValidator(key_fields=['id'])
    
    # First record - valid
    result1 = validator.validate({'id': '1', 'name': 'John'})
    assert result1.is_valid
    
    # Second record with different ID - valid
    result2 = validator.validate({'id': '2', 'name': 'Jane'})
    assert result2.is_valid
    
    # Third record with duplicate ID - invalid
    result3 = validator.validate({'id': '1', 'name': 'Bob'})
    assert not result3.is_valid
    assert 'Duplicate' in result3.errors[0]


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])

