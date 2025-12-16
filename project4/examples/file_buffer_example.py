"""
File Buffer Example

This example shows how to use file-based buffer for
persistent quarantine storage.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors import CSVExtractor
from src.validators import SchemaValidator, ConstraintValidator, RangeConstraint
from src.loaders import JSONLoader
from src.buffer import JSONFileBuffer
from src.pipeline import ETLPipeline, PipelineConfig
from src.utils import DataGenerator, setup_logging


def main():
    """Demonstrate file buffer usage."""
    setup_logging(level='INFO')
    
    # Generate test data
    print("Generating test data with errors...")
    generator = DataGenerator(seed=42)
    test_data = generator.generate_dataset(
        record_type='transaction',
        count=100,
        error_rate=0.3,
        error_types=['missing_field', 'invalid_type', 'out_of_range']
    )
    
    input_file = Path('temp_transactions.csv')
    output_file = Path('valid_transactions.json')
    quarantine_file = Path('quarantine/bad_transactions.json')
    
    generator.save_to_csv(test_data, str(input_file))
    
    print(f"\nProcessing {len(test_data)} transactions...")
    
    # Setup pipeline with file buffer
    extractor = CSVExtractor(file_path=str(input_file))
    
    validators = [
        SchemaValidator(schema={
            'transaction_id': {'type': 'str', 'required': True},
            'amount': {'type': 'float', 'required': True},
            'status': {'type': 'str', 'required': True},
        }),
        ConstraintValidator(constraints={
            'amount': [RangeConstraint(min_value=0, max_value=10000)],
        }),
    ]
    
    loader = JSONLoader(file_path=str(output_file))
    
    # Use file buffer for persistence
    buffer = JSONFileBuffer(
        file_path=str(quarantine_file),
        auto_save=True
    )
    
    config = PipelineConfig(stop_on_error=False)
    
    pipeline = ETLPipeline(
        extractor=extractor,
        validators=validators,
        loader=loader,
        buffer=buffer,
        config=config
    )
    
    result = pipeline.run()
    
    # Print results
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Total records: {result.total_records}")
    print(f"Valid records: {result.successful_records}")
    print(f"Invalid records: {result.failed_records}")
    print(f"Quarantined: {result.quarantined_records}")
    print(f"Duration: {result.duration():.2f}s")
    
    if output_file.exists():
        print(f"\n✓ Valid transactions saved to: {output_file}")
    
    if quarantine_file.exists():
        print(f"✓ Quarantined transactions saved to: {quarantine_file}")
        print(f"  (File persisted - can be reviewed later)")
    
    # Demonstrate loading from file
    print("\n" + "="*60)
    print("LOADING QUARANTINE FROM FILE")
    print("="*60)
    
    # Create new buffer instance to load existing file
    buffer2 = JSONFileBuffer(file_path=str(quarantine_file))
    
    print(f"Loaded {buffer2.count()} quarantined records from file")
    
    # Show sample quarantined records
    if buffer2.count() > 0:
        print("\nSample quarantined records:")
        for qr in buffer2.get_quarantined(limit=3):
            print(f"\n  ID: {qr.id}")
            print(f"  Errors: {', '.join(qr.errors)}")
            print(f"  Amount: {qr.record.get('amount', 'N/A')}")
    
    # Cleanup
    input_file.unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print("Note: Quarantine file kept for inspection")
    print(f"To view: cat {quarantine_file}")
    print("="*60)


if __name__ == '__main__':
    main()

