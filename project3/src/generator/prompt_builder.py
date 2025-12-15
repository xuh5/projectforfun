"""Build prompts for OpenAI API to generate synthetic data."""

from typing import Dict, Any, List
from ..schema.parser import SchemaParser


class PromptBuilder:
    """Build detailed prompts for GPT models to generate synthetic JSON data."""
    
    def __init__(self, schema_parser: SchemaParser):
        """
        Initialize prompt builder.
        
        Args:
            schema_parser: SchemaParser instance with loaded schema
        """
        self.schema_parser = schema_parser
    
    def build_prompt(self, count: int = 1) -> str:
        """
        Build a prompt for generating synthetic data.
        
        Args:
            count: Number of records to generate
            
        Returns:
            Complete prompt string for OpenAI API
        """
        schema_name = self.schema_parser.get_name()
        schema_description = self.schema_parser.get_description()
        fields = self.schema_parser.get_fields()
        
        prompt_parts = [
            "You are a synthetic data generator. Generate realistic JSON data based on the following schema.",
            "",
            f"Schema Name: {schema_name}",
        ]
        
        if schema_description:
            prompt_parts.append(f"Description: {schema_description}")
        
        prompt_parts.extend([
            "",
            "Schema Fields:",
            "=" * 50,
        ])
        
        # Add field descriptions
        for field_name, field_info in fields.items():
            field_desc = self.schema_parser.build_field_description(field_name, field_info)
            prompt_parts.append(field_desc)
            prompt_parts.append("")
        
        prompt_parts.extend([
            "=" * 50,
            "",
            "Instructions:",
            "1. Generate realistic, varied data that matches the schema",
            "2. Ensure all required fields are included",
            "3. Follow all constraints (min/max, patterns, enums, etc.)",
            "4. Make the data look authentic and diverse",
            "5. For nested objects, generate complete nested structures",
            "6. For arrays, generate appropriate number of items within constraints",
            "",
        ])
        
        if count == 1:
            prompt_parts.extend([
                "Generate a single JSON object matching this schema.",
                "Return ONLY valid JSON, no markdown, no code blocks, no explanations.",
            ])
        else:
            prompt_parts.extend([
                f"Generate {count} JSON objects matching this schema.",
                "Return a JSON array containing all objects.",
                "Return ONLY valid JSON, no markdown, no code blocks, no explanations.",
            ])
        
        return "\n".join(prompt_parts)
    
    def build_system_prompt(self) -> str:
        """Build system prompt for OpenAI API."""
        return (
            "You are a synthetic data generator. Your task is to generate realistic, "
            "diverse JSON data that matches provided schemas exactly. Always return "
            "valid JSON without any markdown formatting or explanatory text."
        )

