"""Schema parser for JSON schema configuration files."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SchemaParser:
    """Parse and validate schema configuration files."""
    
    def __init__(self, schema_path: str):
        """
        Initialize schema parser.
        
        Args:
            schema_path: Path to JSON schema configuration file
        """
        self.schema_path = Path(schema_path)
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        self.schema = self._load_schema()
        self._validate_schema_structure()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load schema from JSON file."""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
    
    def _validate_schema_structure(self) -> None:
        """Validate basic schema structure."""
        if not isinstance(self.schema, dict):
            raise ValueError("Schema must be a JSON object")
        
        if "fields" not in self.schema:
            raise ValueError("Schema must contain a 'fields' key")
        
        if not isinstance(self.schema["fields"], dict):
            raise ValueError("Schema 'fields' must be a JSON object")
    
    def get_name(self) -> str:
        """Get schema name."""
        return self.schema.get("name", "Unknown")
    
    def get_description(self) -> str:
        """Get schema description."""
        return self.schema.get("description", "")
    
    def get_fields(self) -> Dict[str, Any]:
        """Get all fields from schema."""
        return self.schema.get("fields", {})
    
    def get_field_info(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific field."""
        fields = self.get_fields()
        return fields.get(field_name)
    
    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        required = []
        for field_name, field_info in self.get_fields().items():
            if isinstance(field_info, dict) and field_info.get("required", False):
                required.append(field_name)
        return required
    
    def get_schema_dict(self) -> Dict[str, Any]:
        """Get the full schema dictionary."""
        return self.schema.copy()
    
    def _parse_field_type(self, field_info: Dict[str, Any]) -> str:
        """Parse field type from field info."""
        field_type = field_info.get("type", "string")
        
        # Handle format as type hint
        if "format" in field_info:
            format_type = field_info["format"]
            if format_type in ["email", "uuid", "date", "datetime", "url"]:
                return f"{field_type} ({format_type})"
        
        return field_type
    
    def build_field_description(self, field_name: str, field_info: Dict[str, Any]) -> str:
        """Build a human-readable description of a field."""
        parts = [f"Field: {field_name}"]
        
        field_type = self._parse_field_type(field_info)
        parts.append(f"Type: {field_type}")
        
        if field_info.get("required", False):
            parts.append("Required: Yes")
        
        # Add constraints
        constraints = []
        if "minLength" in field_info:
            constraints.append(f"min length: {field_info['minLength']}")
        if "maxLength" in field_info:
            constraints.append(f"max length: {field_info['maxLength']}")
        if "min" in field_info:
            constraints.append(f"min: {field_info['min']}")
        if "max" in field_info:
            constraints.append(f"max: {field_info['max']}")
        if "pattern" in field_info:
            constraints.append(f"pattern: {field_info['pattern']}")
        if "enum" in field_info:
            constraints.append(f"enum: {field_info['enum']}")
        
        if constraints:
            parts.append(f"Constraints: {', '.join(constraints)}")
        
        # Handle nested objects
        if field_info.get("type") == "object" and "fields" in field_info:
            parts.append("Nested object with fields:")
            for nested_name, nested_info in field_info["fields"].items():
                nested_desc = self.build_field_description(nested_name, nested_info)
                parts.append(f"  {nested_desc}")
        
        # Handle arrays
        if field_info.get("type") == "array":
            items = field_info.get("items", {})
            if isinstance(items, dict):
                parts.append(f"Array items: {self._parse_field_type(items)}")
            if "minItems" in field_info:
                parts.append(f"min items: {field_info['minItems']}")
            if "maxItems" in field_info:
                parts.append(f"max items: {field_info['maxItems']}")
        
        return " | ".join(parts)

