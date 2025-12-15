"""Tests for schema parser."""

import json
import tempfile
from pathlib import Path
import pytest

from src.schema.parser import SchemaParser


def create_temp_schema(schema_dict: dict) -> Path:
    """Create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(schema_dict, f)
        return Path(f.name)


def test_parse_basic_schema():
    """Test parsing a basic schema."""
    schema = {
        "name": "Test",
        "description": "Test schema",
        "fields": {
            "id": {"type": "string", "required": True},
            "name": {"type": "string", "minLength": 2, "maxLength": 50},
        },
    }
    
    schema_path = create_temp_schema(schema)
    parser = SchemaParser(str(schema_path))
    
    assert parser.get_name() == "Test"
    assert parser.get_description() == "Test schema"
    assert len(parser.get_fields()) == 2
    assert "id" in parser.get_fields()
    assert "name" in parser.get_fields()
    
    schema_path.unlink()


def test_get_required_fields():
    """Test getting required fields."""
    schema = {
        "fields": {
            "required1": {"type": "string", "required": True},
            "optional1": {"type": "string"},
            "required2": {"type": "integer", "required": True},
        },
    }
    
    schema_path = create_temp_schema(schema)
    parser = SchemaParser(str(schema_path))
    
    required = parser.get_required_fields()
    assert len(required) == 2
    assert "required1" in required
    assert "required2" in required
    assert "optional1" not in required
    
    schema_path.unlink()


def test_invalid_schema_file():
    """Test error handling for invalid schema file."""
    with pytest.raises(FileNotFoundError):
        SchemaParser("nonexistent.json")


def test_invalid_json():
    """Test error handling for invalid JSON."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json {")
        schema_path = Path(f.name)
    
    with pytest.raises(ValueError):
        SchemaParser(str(schema_path))
    
    schema_path.unlink()


def test_missing_fields():
    """Test error handling for missing fields key."""
    schema = {"name": "Test"}
    
    schema_path = create_temp_schema(schema)
    
    with pytest.raises(ValueError):
        SchemaParser(str(schema_path))
    
    schema_path.unlink()

