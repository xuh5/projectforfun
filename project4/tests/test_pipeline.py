"""Tests for ETL pipeline."""

import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors import CSVExtractor
from src.validators import SchemaValidator
from src.loaders import JSONLinesLoader
from src.buffer import MemoryBuffer
from src.pipeline import ETLPipeline, PipelineConfig
from src.utils import DataGenerator


def test_basic_pipeline():
    """Test basic pipeline execution."""
    # Generate test data
    generator = DataGenerator(seed=42)
    data = generator.generate_dataset(
        record_type='user',
        count=10,
        error_rate=0.3
    )
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        input_file = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        output_file = Path(f.name)
    
    try:
        # Save test data
        generator.save_to_csv(data, str(input_file))
        
        # Create pipeline
        extractor = CSVExtractor(file_path=str(input_file))
        validators = [
            SchemaValidator(schema={
                'first_name': {'type': 'str', 'required': True},
                'last_name': {'type': 'str', 'required': True},
            })
        ]
        loader = JSONLinesLoader(file_path=str(output_file))
        buffer = MemoryBuffer()
        
        pipeline = ETLPipeline(
            extractor=extractor,
            validators=validators,
            loader=loader,
            buffer=buffer
        )
        
        # Run pipeline
        result = pipeline.run()
        
        # Assertions
        assert result.total_records == 10
        assert result.successful_records > 0
        assert result.successful_records + result.failed_records == result.total_records
        
    finally:
        # Cleanup
        input_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)


def test_pipeline_with_quarantine():
    """Test pipeline with quarantine functionality."""
    # Generate data with errors
    generator = DataGenerator(seed=42)
    data = generator.generate_dataset(
        record_type='user',
        count=20,
        error_rate=0.5,
        error_types=['missing_field']
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        input_file = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        output_file = Path(f.name)
    
    try:
        generator.save_to_csv(data, str(input_file))
        
        extractor = CSVExtractor(file_path=str(input_file))
        validators = [
            SchemaValidator(schema={
                'first_name': {'type': 'str', 'required': True},
                'last_name': {'type': 'str', 'required': True},
                'email': {'type': 'str', 'required': True},
            })
        ]
        loader = JSONLinesLoader(file_path=str(output_file))
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
        
        # Should have quarantined some records
        assert buffer.count() > 0
        assert result.quarantined_records == buffer.count()
        assert result.failed_records == buffer.count()
        
        # Check quarantined records have errors
        for qr in buffer.get_quarantined():
            assert len(qr.errors) > 0
        
    finally:
        input_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])

