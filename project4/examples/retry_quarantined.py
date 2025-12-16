"""
Retry Quarantined Records Example

This example demonstrates how to retry quarantined records
after fixing validation issues.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors import JSONLinesExtractor
from src.validators import SchemaValidator, FormatValidator
from src.transformers import DataCleaner, TypeConverter
from src.loaders import JSONLinesLoader
from src.buffer import JSONFileBuffer
from src.pipeline import ETLPipeline, PipelineConfig
from src.utils import DataGenerator, setup_logging


def main():
    """Demonstrate retry functionality."""
    setup_logging(level='INFO')
    
    # Generate test data with errors
    print("Generating test data...")
    generator = DataGenerator(seed=42)
    test_data = generator.generate_dataset(
        record_type='product',
        count=30,
        error_rate=0.5,
        error_types=['missing_field', 'invalid_type', 'out_of_range']
    )
    
    input_file = Path('temp_retry_input.jsonl')
    output_file = Path('temp_retry_output.jsonl')
    quarantine_file = Path('temp_quarantine.json')
    
    generator.save_to_jsonl(test_data, str(input_file))
    
    # First run: Process with validation
    print("\n" + "="*60)
    print("FIRST RUN: Processing with validation")
    print("="*60)
    
    extractor = JSONLinesExtractor(file_path=str(input_file))
    
    validators = [
        SchemaValidator(schema={
            'product_id': {'type': 'str', 'required': True},
            'name': {'type': 'str', 'required': True},
            'price': {'type': 'float', 'required': True},
            'stock': {'type': 'int', 'required': True},
        }),
        FormatValidator(fields={'price': 'number', 'stock': 'integer'}),
    ]
    
    # Add type converter to fix some errors
    transformers = [
        DataCleaner(strip_whitespace=True),
        TypeConverter(conversions={
            'price': float,
            'stock': int,
        }),
    ]
    
    loader = JSONLinesLoader(file_path=str(output_file), mode='w')
    buffer = JSONFileBuffer(file_path=str(quarantine_file))
    
    config = PipelineConfig(stop_on_error=False)
    
    pipeline = ETLPipeline(
        extractor=extractor,
        validators=validators,
        transformers=transformers,
        loader=loader,
        buffer=buffer,
        config=config
    )
    
    result1 = pipeline.run()
    
    print(f"\nFirst run results:")
    print(f"  Total: {result1.total_records}")
    print(f"  Success: {result1.successful_records}")
    print(f"  Failed: {result1.failed_records}")
    print(f"  Quarantined: {result1.quarantined_records}")
    
    # Retry quarantined records
    if buffer.count() > 0:
        print("\n" + "="*60)
        print("RETRY: Processing quarantined records")
        print("="*60)
        
        # Create new pipeline for retry
        # Use append mode for loader to add to existing output
        retry_loader = JSONLinesLoader(file_path=str(output_file), mode='a')
        
        retry_pipeline = ETLPipeline(
            extractor=extractor,  # Won't be used
            validators=validators,
            transformers=transformers,
            loader=retry_loader,
            buffer=buffer,
            config=config
        )
        
        result2 = retry_pipeline.retry_quarantined(max_retries=3)
        
        print(f"\nRetry results:")
        print(f"  Attempted: {result2.total_records}")
        print(f"  Success: {result2.successful_records}")
        print(f"  Still failed: {result2.failed_records}")
        
        # Final statistics
        print("\n" + "="*60)
        print("FINAL STATISTICS")
        print("="*60)
        
        total_success = result1.successful_records + result2.successful_records
        total_processed = result1.total_records
        
        print(f"Total records: {total_processed}")
        print(f"Successfully processed: {total_success}")
        print(f"Still quarantined: {buffer.count()}")
        print(f"Overall success rate: {(total_success / total_processed * 100):.2f}%")
        
        # Show records still in quarantine
        if buffer.count() > 0:
            print("\n" + "="*60)
            print("STILL QUARANTINED")
            print("="*60)
            for qr in buffer.get_quarantined():
                print(f"\n✗ Record: {qr.record.get('name', 'N/A')}")
                print(f"  Retry count: {qr.retry_count}")
                print(f"  Errors: {', '.join(qr.errors)}")
    
    # Cleanup
    input_file.unlink(missing_ok=True)
    quarantine_file.unlink(missing_ok=True)
    
    if output_file.exists():
        print(f"\n✓ Final output: {output_file}")


if __name__ == '__main__':
    main()

