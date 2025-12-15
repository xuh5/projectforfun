# Synthetic JSON Data Generator

A CLI tool that uses OpenAI's GPT models to generate realistic synthetic JSON data based on user-defined schemas.

## Features

- 🎯 **Schema-based generation**: Define your data structure in JSON
- 🤖 **AI-powered**: Uses OpenAI GPT models for realistic data generation
- ✅ **Validation**: Built-in validation against schema constraints
- 🔧 **Flexible**: Support for nested objects, arrays, and complex constraints
- 📝 **CLI interface**: Easy-to-use command-line tool
- 🎨 **Pretty output**: Formatted JSON output with optional file saving

## Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd project3
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   
   Create a `.env` file in the `project3` directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

## Quick Start

### Generate a single record:

```bash
python -m src.main generate --schema examples/user_schema.json
```

### Generate multiple records:

```bash
python -m src.main generate --schema examples/user_schema.json --count 5
```

### Save to file:

```bash
python -m src.main generate --schema examples/user_schema.json --count 10 --output output.json
```

### Validate existing data:

```bash
python -m src.main validate --schema examples/user_schema.json --data output.json
```

## Schema Format

Schemas are defined in JSON format with the following structure:

```json
{
  "name": "SchemaName",
  "description": "Description of what this schema represents",
  "fields": {
    "fieldName": {
      "type": "string|integer|number|boolean|object|array",
      "format": "email|uuid|date|datetime|url (optional)",
      "required": true|false,
      "minLength": 2 (for strings),
      "maxLength": 50 (for strings),
      "min": 0 (for numbers),
      "max": 100 (for numbers),
      "pattern": "^regex$" (for strings),
      "enum": ["value1", "value2"] (for strings),
      "minItems": 1 (for arrays),
      "maxItems": 10 (for arrays),
      "fields": { ... } (for objects - nested schema),
      "items": { ... } (for arrays - item schema)
    }
  }
}
```

### Field Types

- **string**: Text data
- **integer**: Whole numbers
- **number**: Decimal numbers
- **boolean**: True/false values
- **object**: Nested JSON objects
- **array**: Lists of items

### Formats

- **email**: Email address validation
- **uuid**: UUID format validation
- **date**: Date in YYYY-MM-DD format
- **datetime**: Date and time
- **url**: URL format validation

### Example Schema

See `examples/user_schema.json` for a complete example with various field types and constraints.

## CLI Commands

### `generate`

Generate synthetic JSON data from a schema.

**Options:**
- `--schema, -s`: Path to JSON schema file (required)
- `--count, -c`: Number of records to generate (default: 1)
- `--output, -o`: Output file path (default: print to console)
- `--model, -m`: OpenAI model to use (default: from config)
- `--api-key`: OpenAI API key (default: from env)
- `--validate/--no-validate`: Validate generated data (default: True)
- `--temperature, -t`: Sampling temperature 0.0-2.0 (default: 0.7)

**Examples:**
```bash
# Generate one record
python -m src.main generate -s examples/user_schema.json

# Generate 10 records and save to file
python -m src.main generate -s examples/product_schema.json -c 10 -o products.json

# Use a different model
python -m src.main generate -s examples/user_schema.json -m gpt-4
```

### `validate`

Validate existing JSON data against a schema.

**Options:**
- `--schema, -s`: Path to JSON schema file (required)
- `--data, -d`: Path to JSON data file to validate (required)

**Example:**
```bash
python -m src.main validate -s examples/user_schema.json -d output.json
```

## Example Schemas

The `examples/` directory contains sample schemas:

- **user_schema.json**: User profile with nested address and tags
- **product_schema.json**: E-commerce product information
- **nested_schema.json**: Complex order with nested customer and items

## Project Structure

```
project3/
├── src/
│   ├── main.py              # CLI entry point
│   ├── config.py            # Configuration management
│   ├── schema/
│   │   ├── parser.py        # Schema parsing
│   │   └── validator.py     # Data validation
│   ├── generator/
│   │   ├── openai_client.py # OpenAI API client
│   │   └── prompt_builder.py # Prompt generation
│   └── output/
│       └── handler.py       # Output formatting
├── examples/                # Example schema files
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Advanced Usage

### Custom Temperature

Control randomness in generation:
```bash
# More deterministic (lower temperature)
python -m src.main generate -s examples/user_schema.json -t 0.3

# More creative (higher temperature)
python -m src.main generate -s examples/user_schema.json -t 1.2
```

### Skip Validation

If you want to generate data without validation:
```bash
python -m src.main generate -s examples/user_schema.json --no-validate
```

### Using Different Models

```bash
# Use GPT-4 for higher quality
python -m src.main generate -s examples/user_schema.json -m gpt-4

# Use GPT-3.5 for faster/cheaper generation
python -m src.main generate -s examples/user_schema.json -m gpt-3.5-turbo
```

## Troubleshooting

### "OPENAI_API_KEY is required"

Make sure you've created a `.env` file with your OpenAI API key:
```env
OPENAI_API_KEY=sk-...
```

### "Invalid JSON in schema file"

Check that your schema file is valid JSON. You can validate it with:
```bash
python -m json.tool examples/user_schema.json
```

### "Failed to parse JSON response"

The AI model sometimes returns JSON wrapped in markdown. The tool automatically handles this, but if it persists, try:
- Using a different model (e.g., `gpt-4`)
- Lowering the temperature
- Simplifying your schema

### Validation Errors

If validation fails, check:
- All required fields are present
- Field types match (string, integer, etc.)
- Constraints are met (min/max, patterns, enums)
- Nested objects match their schema

## License

This project is for educational and development purposes.

