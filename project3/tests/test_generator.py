"""Tests for generator components."""

import json
import tempfile
from pathlib import Path
import pytest

from src.schema.parser import SchemaParser
from src.generator.prompt_builder import PromptBuilder


def create_temp_schema(schema_dict: dict) -> Path:
    """Create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(schema_dict, f)
        return Path(f.name)


def test_prompt_builder_basic():
    """Test prompt builder creates valid prompts."""
    schema = {
        "name": "TestUser",
        "description": "Test user schema",
        "fields": {
            "id": {"type": "string", "required": True},
            "name": {"type": "string", "minLength": 2},
        },
    }
    
    schema_path = create_temp_schema(schema)
    parser = SchemaParser(str(schema_path))
    builder = PromptBuilder(parser)
    
    prompt = builder.build_prompt(count=1)
    
    assert "TestUser" in prompt
    assert "Test user schema" in prompt
    assert "id" in prompt
    assert "name" in prompt
    assert "required" in prompt.lower()
    
    schema_path.unlink()


def test_prompt_builder_multiple():
    """Test prompt builder for multiple records."""
    schema = {
        "name": "Test",
        "fields": {"id": {"type": "string"}},
    }
    
    schema_path = create_temp_schema(schema)
    parser = SchemaParser(str(schema_path))
    builder = PromptBuilder(parser)
    
    prompt = builder.build_prompt(count=5)
    
    assert "5" in prompt
    assert "array" in prompt.lower() or "objects" in prompt.lower()
    
    schema_path.unlink()


def test_prompt_builder_system_prompt():
    """Test system prompt generation."""
    schema = {
        "name": "Test",
        "fields": {"id": {"type": "string"}},
    }
    
    schema_path = create_temp_schema(schema)
    parser = SchemaParser(str(schema_path))
    builder = PromptBuilder(parser)
    
    system_prompt = builder.build_system_prompt()
    
    assert "synthetic data" in system_prompt.lower()
    assert "json" in system_prompt.lower()
    
    schema_path.unlink()

