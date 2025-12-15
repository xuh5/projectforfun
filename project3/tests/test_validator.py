"""Tests for schema validator."""

import pytest

from src.schema.validator import SchemaValidator


def test_validate_required_fields():
    """Test validation of required fields."""
    schema = {
        "fields": {
            "required1": {"type": "string", "required": True},
            "optional1": {"type": "string"},
        },
    }
    
    validator = SchemaValidator(schema)
    
    # Missing required field
    data = {"optional1": "value"}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    assert any("required1" in err for err in errors)
    
    # All required fields present
    data = {"required1": "value", "optional1": "value2"}
    is_valid, errors = validator.validate(data)
    assert is_valid
    assert len(errors) == 0


def test_validate_string_constraints():
    """Test validation of string constraints."""
    schema = {
        "fields": {
            "name": {
                "type": "string",
                "minLength": 2,
                "maxLength": 10,
                "pattern": "^[A-Za-z]+$",
            },
        },
    }
    
    validator = SchemaValidator(schema)
    
    # Too short
    data = {"name": "A"}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Too long
    data = {"name": "A" * 11}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Invalid pattern
    data = {"name": "123"}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Valid
    data = {"name": "ValidName"}
    is_valid, errors = validator.validate(data)
    assert is_valid


def test_validate_number_constraints():
    """Test validation of number constraints."""
    schema = {
        "fields": {
            "age": {"type": "integer", "min": 18, "max": 100},
            "price": {"type": "number", "min": 0.01, "max": 1000.0},
        },
    }
    
    validator = SchemaValidator(schema)
    
    # Below min
    data = {"age": 17}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Above max
    data = {"age": 101}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Valid
    data = {"age": 25, "price": 99.99}
    is_valid, errors = validator.validate(data)
    assert is_valid


def test_validate_format():
    """Test validation of format constraints."""
    schema = {
        "fields": {
            "email": {"type": "string", "format": "email"},
            "uuid": {"type": "string", "format": "uuid"},
        },
    }
    
    validator = SchemaValidator(schema)
    
    # Invalid email
    data = {"email": "not-an-email"}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Valid email
    data = {"email": "test@example.com"}
    is_valid, errors = validator.validate(data)
    assert is_valid


def test_validate_nested_object():
    """Test validation of nested objects."""
    schema = {
        "fields": {
            "address": {
                "type": "object",
                "fields": {
                    "street": {"type": "string", "required": True},
                    "city": {"type": "string"},
                },
            },
        },
    }
    
    validator = SchemaValidator(schema)
    
    # Missing required nested field
    data = {"address": {"city": "New York"}}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Valid nested object
    data = {"address": {"street": "123 Main St", "city": "New York"}}
    is_valid, errors = validator.validate(data)
    assert is_valid


def test_validate_array():
    """Test validation of arrays."""
    schema = {
        "fields": {
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 5,
            },
        },
    }
    
    validator = SchemaValidator(schema)
    
    # Too few items
    data = {"tags": []}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Too many items
    data = {"tags": ["a", "b", "c", "d", "e", "f"]}
    is_valid, errors = validator.validate(data)
    assert not is_valid
    
    # Valid array
    data = {"tags": ["tag1", "tag2", "tag3"]}
    is_valid, errors = validator.validate(data)
    assert is_valid

