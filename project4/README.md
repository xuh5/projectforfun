# ETL Bad Data Handler & Buffer System

A powerful, extensible Python framework for building ETL (Extract, Transform, Load) pipelines with comprehensive bad data handling, validation, and quarantine capabilities.

## 🎯 Features

- **Pluggable Architecture**: Easily extend with custom extractors, validators, transformers, and loaders
- **Comprehensive Validation**: Built-in validators for format, schema, constraints, and duplicates
- **Error Handling**: Intelligent quarantine system for bad data with retry capabilities
- **Multiple Data Sources**: Support for CSV, JSON, JSON Lines, and REST APIs
- **Flexible Storage**: Memory or file-based buffer for quarantined records
- **Production Ready**: Logging, error reporting, and performance metrics built-in

## 📦 Installation

```bash
# Clone or copy the project
cd project4

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

Here's a minimal example to get started:

```python
from src.extractors import CSVExtractor
from src.validators import SchemaValidator
from src.loaders import JSONLinesLoader
from src.buffer import MemoryBuffer
from src.pipeline import ETLPipeline

# Configure components
extractor = CSVExtractor(file_path='input.csv')

validators = [
    SchemaValidator(schema={
        'name': {'type': 'str', 'required': True},
        'email': {'type': 'str', 'required': True},
        'age': {'type': 'int', 'required': False},
    })
]

loader = JSONLinesLoader(file_path='output.jsonl')
buffer = MemoryBuffer()

# Create and run pipeline
pipeline = ETLPipeline(
    extractor=extractor,
    validators=validators,
    loader=loader,
    buffer=buffer
)

result = pipeline.run()

print(f"Processed: {result.total_records}")
print(f"Success: {result.successful_records}")
print(f"Failed: {result.failed_records}")
```

## 📚 Core Components

### Extractors

Extract data from various sources:

- **CSVExtractor**: Read CSV files
- **JSONExtractor**: Read JSON files
- **JSONLinesExtractor**: Read JSONL files
- **APIExtractor**: Fetch from REST APIs
- **RESTAPIExtractor**: REST APIs with pagination

### Validators

Validate data quality:

- **SchemaValidator**: Validate field types and structure
- **FormatValidator**: Validate formats (email, date, number, etc.)
- **ConstraintValidator**: Apply business rules (range, regex, enum)
- **DuplicateValidator**: Detect duplicate records
- **RequiredFieldValidator**: Ensure required fields exist

### Transformers

Transform and clean data:

- **DataCleaner**: Strip whitespace, handle empty strings
- **FieldMapper**: Rename fields
- **DefaultValueFiller**: Fill missing values with defaults
- **TypeConverter**: Convert field types
- **FieldRemover**: Remove unwanted fields

### Loaders

Load data to destinations:

- **CSVLoader**: Write to CSV files
- **JSONLoader**: Write to JSON files
- **JSONLinesLoader**: Write to JSONL files
- **ConsoleLoader**: Print to console (for debugging)

### Buffers

Store quarantined records:

- **MemoryBuffer**: In-memory storage (development/testing)
- **JSONFileBuffer**: Persistent file storage (production)

## 🔧 Advanced Usage

### Custom Validators

Create custom validators by extending the `Validator` base class:

```python
from src.core import Validator, ValidationResult

class EmailDomainValidator(Validator):
    def __init__(self, allowed_domains: list[str]):
        super().__init__()
        self.allowed_domains = set(allowed_domains)
    
    def validate(self, record: dict) -> ValidationResult:
        errors = []
        
        if 'email' in record:
            domain = record['email'].split('@')[-1]
            if domain not in self.allowed_domains:
                errors.append(f"Domain '{domain}' not allowed")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )

# Use in pipeline
validators = [
    EmailDomainValidator(allowed_domains=['company.com'])
]
```

### Retry Quarantined Records

```python
# First run
result1 = pipeline.run()
print(f"Quarantined: {result1.quarantined_records}")

# Retry failed records
result2 = pipeline.retry_quarantined(max_retries=3)
print(f"Recovered: {result2.successful_records}")
```

### File-Based Buffer

Use persistent storage for quarantined records:

```python
from src.buffer import JSONFileBuffer

buffer = JSONFileBuffer(
    file_path='quarantine/bad_records.json',
    auto_save=True
)

# Records persist across runs
# Load existing quarantine
buffer2 = JSONFileBuffer(file_path='quarantine/bad_records.json')
print(f"Loaded {buffer2.count()} quarantined records")
```

### Pipeline Configuration

```python
from src.pipeline import PipelineConfig

config = PipelineConfig(
    stop_on_error=False,      # Continue on errors
    max_errors=100,            # Stop after 100 errors
    enable_retry=True,         # Enable retry
    max_retries=3              # Max 3 retries per record
)

pipeline = ETLPipeline(..., config=config)
```

## 📖 Examples

The `examples/` directory contains complete working examples:

- **basic_pipeline.py**: Simple ETL pipeline with validation
- **custom_validator.py**: How to create custom validators
- **retry_quarantined.py**: Retry failed records
- **file_buffer_example.py**: Persistent quarantine storage

Run examples:

```bash
python examples/basic_pipeline.py
python examples/custom_validator.py
python examples/retry_quarantined.py
python examples/file_buffer_example.py
```

## 🧪 Generate Test Data

Use the built-in data generator to create test datasets:

```python
from src.utils import DataGenerator

generator = DataGenerator(seed=42)

# Generate data with various error types
data = generator.generate_dataset(
    record_type='user',        # 'user', 'transaction', or 'product'
    count=100,
    error_rate=0.3,            # 30% of records have errors
    error_types=[
        'missing_field',
        'invalid_format',
        'invalid_type',
        'out_of_range'
    ]
)

# Save to file
generator.save_to_csv(data, 'test_data.csv')
generator.save_to_json(data, 'test_data.json')
generator.save_to_jsonl(data, 'test_data.jsonl')
```

## 🏗️ Architecture

```
┌─────────────┐
│  Extractor  │ ← Pluggable (CSV, JSON, API, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validator  │ ← Pluggable (chain multiple validators)
└──────┬──────┘
       │
       ├─► Valid ────────► Transformer ────────► Loader
       │                      ↑                     ↑
       │                      └── Pluggable ───────┘
       │
       └─► Invalid ─────► Buffer/Quarantine ───► Error Handler
                             ↑
                             └── Pluggable (Memory or File)
```

## 📝 Project Structure

```
project4/
├── src/
│   ├── core/              # Core interfaces and base classes
│   │   ├── extractor.py
│   │   ├── validator.py
│   │   ├── transformer.py
│   │   ├── loader.py
│   │   └── buffer.py
│   ├── extractors/        # Built-in extractors
│   │   ├── file_extractor.py
│   │   └── api_extractor.py
│   ├── validators/        # Built-in validators
│   │   ├── format_validator.py
│   │   ├── schema_validator.py
│   │   ├── constraint_validator.py
│   │   └── duplicate_validator.py
│   ├── transformers/      # Built-in transformers
│   │   └── data_cleaner.py
│   ├── loaders/          # Built-in loaders
│   │   ├── file_loader.py
│   │   └── console_loader.py
│   ├── buffer/           # Buffer implementations
│   │   ├── memory_buffer.py
│   │   └── file_buffer.py
│   ├── pipeline/         # ETL pipeline orchestration
│   │   └── etl_pipeline.py
│   └── utils/            # Utilities
│       ├── data_generator.py
│       └── logger.py
├── examples/             # Example scripts
├── tests/               # Unit tests
├── requirements.txt
└── README.md
```

## 🔌 Extending the Framework

### Add Custom Extractor

```python
from src.core import Extractor

class DatabaseExtractor(Extractor):
    def __init__(self, connection_string: str):
        super().__init__()
        self.connection_string = connection_string
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        # Connect to database
        # Yield records
        pass
```

### Add Custom Transformer

```python
from src.core import Transformer

class EncryptionTransformer(Transformer):
    def transform(self, record: Dict[str, Any]) -> Dict[str, Any]:
        # Encrypt sensitive fields
        record['ssn'] = encrypt(record['ssn'])
        return record
```

### Add Custom Loader

```python
from src.core import Loader

class DatabaseLoader(Loader):
    def load(self, record: Dict[str, Any]) -> bool:
        # Insert into database
        # Return True if successful
        pass
```

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest tests/

# With coverage
pytest --cov=src tests/
```

## 🤝 Contributing

This is an extensible framework designed to be customized for your needs:

1. Create custom components by extending base classes
2. Add new validators, transformers, extractors, or loaders
3. Share reusable components with the community

## 📄 License

This project is provided as-is for educational and commercial use.

## 🎓 Use Cases

- **Data Migration**: Migrate data between systems with validation
- **Data Quality**: Identify and quarantine bad data for review
- **ETL Pipelines**: Build production ETL workflows with error handling
- **Data Cleaning**: Clean and standardize incoming data
- **API Integration**: Extract and validate data from APIs
- **Testing**: Generate test data with various error scenarios

## 💡 Tips

1. **Start Simple**: Begin with basic validators and add complexity as needed
2. **Use File Buffer**: In production, use `JSONFileBuffer` for persistence
3. **Chain Validators**: Combine multiple validators for comprehensive checks
4. **Monitor Quarantine**: Regularly review quarantined records
5. **Enable Retry**: Use retry for transient errors
6. **Log Everything**: Enable detailed logging for debugging

## 🆘 Troubleshooting

**Q: Pipeline processes no records**
- Check file paths are correct
- Verify file format matches extractor type
- Enable DEBUG logging to see details

**Q: All records fail validation**
- Review validator configuration
- Check schema matches your data structure
- Use `ConsoleLoader` to inspect records

**Q: Quarantine file not persisting**
- Ensure directory exists
- Check file permissions
- Verify `auto_save=True` for `JSONFileBuffer`

## 📞 Support

For questions and issues:
- Review examples in `examples/` directory
- Check inline documentation in source code
- Enable DEBUG logging for detailed output

---

**Built with ❤️ for robust data processing**

