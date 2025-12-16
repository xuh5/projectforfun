"""
Basic ETL Pipeline Example

This example demonstrates a simple ETL pipeline that:
1. Extracts data from a CSV file
2. Validates data format and schema
3. Transforms data by cleaning and filling defaults
4. Loads data to an output file
5. Quarantines bad records
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import ValidationResult
from src.extractors import CSVExtractor
from src.validators import (
    SchemaValidator,
    FormatValidator,
    RequiredFieldValidator
)
from src.transformers import DataCleaner, DefaultValueFiller
from src.loaders import JSONLinesLoader, ConsoleLoader
from src.buffer import MemoryBuffer
from src.pipeline import ETLPipeline, PipelineConfig
from src.utils import DataGenerator, setup_logging


def main():
    # Setup logging
    setup_logging(level='INFO')
    
    # Generate test data with errors
    print("Generating test data with errors...")
    generator = DataGenerator(seed=42)
    test_data = generator.generate_dataset(
        record_type='user',
        count=50,
        error_rate=0.3,
        error_types=['missing_field', 'invalid_format', 'invalid_type', 'out_of_range']
    )
    
    # Save test data to CSV
    input_file = Path('temp_input.csv')
    generator.save_to_csv(test_data, str(input_file))
    print(f"Generated {len(test_data)} records to {input_file}")
    
    # Configure pipeline components
    print("\nConfiguring ETL pipeline...")
    
    # Extractor: Read from CSV
    extractor = CSVExtractor(file_path=str(input_file))
    
    # Validators: Check schema, format, and required fields
    validators = [
        RequiredFieldValidator(required_fields=['first_name', 'last_name', 'email']),
        SchemaValidator(schema={
            'first_name': {'type': 'str', 'required': True},
            'last_name': {'type': 'str', 'required': True},
            'email': {'type': 'str', 'required': True},
            'age': {'type': 'int', 'required': False, 'nullable': True},
            'is_active': {'type': 'bool', 'required': False, 'nullable': True},
        }),
        FormatValidator(fields={'email': 'email', 'age': 'integer'}),
    ]
    
    # Transformers: Clean data and fill defaults
    transformers = [
        DataCleaner(strip_whitespace=True, remove_empty_strings=True),
        DefaultValueFiller(defaults={'is_active': True, 'age': 0}),
    ]
    
    # Loader: Write to JSON Lines file
    output_file = Path('output.jsonl')
    loader = JSONLinesLoader(file_path=str(output_file))
    
    # Buffer: Store bad records
    buffer = MemoryBuffer()
    
    # Pipeline configuration
    config = PipelineConfig(
        stop_on_error=False,
        max_errors=None,  # Process all records
    )
    
    # Create and run pipeline
    print("\nRunning ETL pipeline...")
    pipeline = ETLPipeline(
        extractor=extractor,
        validators=validators,
        transformers=transformers,
        loader=loader,
        buffer=buffer,
        config=config
    )
    
    result = pipeline.run()
    
    # Print results
    print("\n" + "="*60)
    print("PIPELINE RESULTS")
    print("="*60)
    print(f"Total records processed: {result.total_records}")
    print(f"Successful records: {result.successful_records}")
    print(f"Failed records: {result.failed_records}")
    print(f"Quarantined records: {result.quarantined_records}")
    print(f"Success rate: {result.success_rate():.2f}%")
    print(f"Duration: {result.duration():.2f} seconds")
    
    # Show quarantined records
    if buffer.count() > 0:
        print("\n" + "="*60)
        print("QUARANTINED RECORDS (First 5)")
        print("="*60)
        for qr in buffer.get_quarantined(limit=5):
            print(f"\nRecord ID: {qr.id}")
            print(f"Errors: {', '.join(qr.errors)}")
            print(f"Data: {qr.record}")
    
    # Cleanup
    input_file.unlink(missing_ok=True)
    if output_file.exists():
        print(f"\n✓ Output written to: {output_file}")
    
    print("\n" + "="*60)
    print("Done!")
    print("="*60)


if __name__ == '__main__':
    main()

