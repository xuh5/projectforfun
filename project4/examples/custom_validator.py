"""
Custom Validator Example

This example shows how to create custom validators
by extending the Validator base class.
"""

import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import Validator, ValidationResult
from src.extractors import CSVExtractor
from src.loaders import ConsoleLoader
from src.buffer import MemoryBuffer
from src.pipeline import ETLPipeline, PipelineConfig
from src.utils import DataGenerator, setup_logging


class EmailDomainValidator(Validator):
    """Custom validator to check email domain."""
    
    def __init__(self, allowed_domains: list[str], config: Dict[str, Any] = None):
        super().__init__(config)
        self.allowed_domains = set(allowed_domains)
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate email domain."""
        errors = []
        
        if 'email' in record:
            email = record['email']
            if isinstance(email, str) and '@' in email:
                domain = email.split('@')[-1]
                if domain not in self.allowed_domains:
                    errors.append(
                        f"Email domain '{domain}' not in allowed list: {self.allowed_domains}"
                    )
            else:
                errors.append("Invalid email format")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors
        )


class AgeRangeValidator(Validator):
    """Custom validator for age range with custom logic."""
    
    def __init__(self, min_age: int = 18, max_age: int = 100, config: Dict[str, Any] = None):
        super().__init__(config)
        self.min_age = min_age
        self.max_age = max_age
    
    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate age is within range."""
        errors = []
        warnings = []
        
        if 'age' not in record:
            warnings.append("Age field is missing")
            return ValidationResult(
                is_valid=True,
                record=record,
                errors=errors,
                warnings=warnings
            )
        
        age = record['age']
        
        try:
            age = int(age)
            
            if age < self.min_age:
                errors.append(f"Age {age} is below minimum age {self.min_age}")
            elif age > self.max_age:
                errors.append(f"Age {age} is above maximum age {self.max_age}")
            elif age < 21:
                warnings.append(f"Age {age} is below 21 (minor restrictions may apply)")
        
        except (ValueError, TypeError):
            errors.append(f"Age must be a number, got: {age}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            record=record,
            errors=errors,
            warnings=warnings
        )


def main():
    """Run example with custom validators."""
    setup_logging(level='INFO')
    
    print("Generating test data...")
    generator = DataGenerator(seed=42)
    test_data = generator.generate_dataset(
        record_type='user',
        count=20,
        error_rate=0.4,
        error_types=['invalid_email', 'out_of_range']
    )
    
    # Save to CSV
    input_file = Path('temp_custom_validator.csv')
    generator.save_to_csv(test_data, str(input_file))
    
    print("\nRunning pipeline with custom validators...")
    
    # Setup pipeline with custom validators
    extractor = CSVExtractor(file_path=str(input_file))
    
    validators = [
        EmailDomainValidator(allowed_domains=['example.com', 'test.com']),
        AgeRangeValidator(min_age=18, max_age=100),
    ]
    
    loader = ConsoleLoader(format='simple', max_length=100)
    buffer = MemoryBuffer()
    
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
    print("RESULTS")
    print("="*60)
    print(f"Total: {result.total_records}")
    print(f"Success: {result.successful_records}")
    print(f"Failed: {result.failed_records}")
    print(f"Success rate: {result.success_rate():.2f}%")
    
    # Show quarantined records with custom validator errors
    if buffer.count() > 0:
        print("\n" + "="*60)
        print("QUARANTINED RECORDS")
        print("="*60)
        for qr in buffer.get_quarantined():
            print(f"\n✗ Record: {qr.record.get('email', 'N/A')}")
            for error in qr.errors:
                print(f"  - {error}")
    
    # Cleanup
    input_file.unlink(missing_ok=True)


if __name__ == '__main__':
    main()

