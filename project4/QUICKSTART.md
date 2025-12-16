# Quick Start Guide

Get up and running with the ETL Bad Data Handler in 5 minutes!

## Installation

```bash
cd project4
pip install -r requirements.txt
```

## Run Your First Pipeline

### Step 1: Generate Test Data

```python
from src.utils import DataGenerator

generator = DataGenerator(seed=42)
data = generator.generate_dataset(
    record_type='user',
    count=100,
    error_rate=0.2  # 20% bad data
)

generator.save_to_csv(data, 'input.csv')
```

### Step 2: Create Pipeline

```python
from src.extractors import CSVExtractor
from src.validators import SchemaValidator
from src.loaders import ConsoleLoader
from src.buffer import MemoryBuffer
from src.pipeline import ETLPipeline

# Extract from CSV
extractor = CSVExtractor(file_path='input.csv')

# Validate schema
validators = [
    SchemaValidator(schema={
        'first_name': {'type': 'str', 'required': True},
        'last_name': {'type': 'str', 'required': True},
        'email': {'type': 'str', 'required': True},
    })
]

# Print to console (for testing)
loader = ConsoleLoader(format='pretty')

# Store bad records
buffer = MemoryBuffer()

# Run pipeline
pipeline = ETLPipeline(
    extractor=extractor,
    validators=validators,
    loader=loader,
    buffer=buffer
)

result = pipeline.run()
```

### Step 3: View Results

```python
print(f"Total: {result.total_records}")
print(f"Success: {result.successful_records}")
print(f"Failed: {result.failed_records}")

# Check quarantined records
for qr in buffer.get_quarantined(limit=5):
    print(f"Errors: {qr.errors}")
    print(f"Record: {qr.record}")
```

## Run Examples

Try the pre-built examples:

```bash
# Basic pipeline
python examples/basic_pipeline.py

# Custom validators
python examples/custom_validator.py

# Retry failed records
python examples/retry_quarantined.py

# Persistent storage
python examples/file_buffer_example.py
```

## Common Patterns

### Pattern 1: CSV to JSON with Validation

```python
from src.extractors import CSVExtractor
from src.validators import FormatValidator, RequiredFieldValidator
from src.loaders import JSONLoader
from src.pipeline import ETLPipeline

pipeline = ETLPipeline(
    extractor=CSVExtractor('input.csv'),
    validators=[
        RequiredFieldValidator(['id', 'name', 'email']),
        FormatValidator(fields={'email': 'email'})
    ],
    loader=JSONLoader('output.json')
)

pipeline.run()
```

### Pattern 2: API to Database (conceptual)

```python
from src.extractors import RESTAPIExtractor
from src.validators import SchemaValidator
# from custom_loaders import DatabaseLoader

pipeline = ETLPipeline(
    extractor=RESTAPIExtractor(
        url='https://api.example.com/users',
        pagination_type='page',
        page_size=100
    ),
    validators=[
        SchemaValidator(schema={...})
    ],
    # loader=DatabaseLoader(connection_string='...')
)
```

### Pattern 3: Data Cleaning Pipeline

```python
from src.transformers import DataCleaner, DefaultValueFiller, FieldMapper

pipeline = ETLPipeline(
    extractor=...,
    transformers=[
        DataCleaner(strip_whitespace=True),
        FieldMapper(field_map={'old_name': 'new_name'}),
        DefaultValueFiller(defaults={'status': 'active'})
    ],
    loader=...
)
```

## Next Steps

1. **Read the full [README.md](README.md)** for detailed documentation
2. **Explore [examples/](examples/)** directory for more use cases
3. **Create custom validators** for your specific needs
4. **Build production pipelines** with file buffers and retry logic

## Tips

- Start with `ConsoleLoader` for debugging
- Use `MemoryBuffer` for development
- Switch to `JSONFileBuffer` for production
- Chain multiple validators for comprehensive checks
- Enable logging: `from src.utils import setup_logging; setup_logging('DEBUG')`

## Troubleshooting

**Import errors?**
```bash
# Make sure you're in the project4 directory
cd project4
python examples/basic_pipeline.py
```

**No records processed?**
- Check file paths
- Verify file format
- Enable DEBUG logging

**All records failing?**
- Review validator configuration
- Check schema matches data
- Use ConsoleLoader to inspect records

---

Happy data processing! 🚀

