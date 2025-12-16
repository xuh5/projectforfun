"""ETL Pipeline orchestration and execution."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from ..core import Extractor, Validator, Transformer, Loader, Buffer, ValidationResult


logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for ETL pipeline."""
    
    stop_on_error: bool = False
    """Whether to stop the pipeline on first error."""
    
    max_errors: Optional[int] = None
    """Maximum number of errors before stopping pipeline."""
    
    enable_retry: bool = False
    """Whether to enable retry of quarantined records."""
    
    max_retries: int = 3
    """Maximum number of retries per record."""
    
    batch_size: Optional[int] = None
    """Batch size for loading (None = load one at a time)."""


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    
    total_records: int = 0
    """Total records processed."""
    
    successful_records: int = 0
    """Successfully processed records."""
    
    failed_records: int = 0
    """Failed records."""
    
    quarantined_records: int = 0
    """Records quarantined for later review."""
    
    started_at: Optional[datetime] = None
    """Pipeline start time."""
    
    completed_at: Optional[datetime] = None
    """Pipeline completion time."""
    
    errors: List[str] = field(default_factory=list)
    """List of errors encountered."""
    
    def duration(self) -> float:
        """Get pipeline duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_records == 0:
            return 0.0
        return (self.successful_records / self.total_records) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_records": self.total_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "quarantined_records": self.quarantined_records,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration(),
            "success_rate": self.success_rate(),
            "errors": self.errors,
        }


class ETLPipeline:
    """
    Main ETL pipeline orchestrator.
    
    Coordinates extraction, validation, transformation, and loading
    with error handling and quarantine support.
    """
    
    def __init__(
        self,
        extractor: Extractor,
        validators: List[Validator],
        loader: Loader,
        buffer: Optional[Buffer] = None,
        transformers: Optional[List[Transformer]] = None,
        config: Optional[PipelineConfig] = None,
    ):
        """
        Initialize the pipeline.
        
        Args:
            extractor: Data extractor
            validators: List of validators
            loader: Data loader
            buffer: Optional buffer for quarantine
            transformers: Optional list of transformers
            config: Optional pipeline configuration
        """
        self.extractor = extractor
        self.validators = validators
        self.loader = loader
        self.buffer = buffer
        self.transformers = transformers or []
        self.config = config or PipelineConfig()
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def run(self) -> PipelineResult:
        """
        Run the ETL pipeline.
        
        Returns:
            PipelineResult with execution statistics
        """
        result = PipelineResult(started_at=datetime.utcnow())
        
        try:
            self.logger.info("Starting ETL pipeline")
            
            for record in self.extractor.extract():
                result.total_records += 1
                
                # Validate
                validation_result = self._validate_record(record)
                
                if not validation_result.is_valid:
                    result.failed_records += 1
                    self._handle_failed_record(record, validation_result, result)
                    
                    # Check if we should stop
                    if self._should_stop(result):
                        break
                    
                    continue
                
                # Transform
                try:
                    transformed_record = self._transform_record(validation_result.record)
                except Exception as e:
                    self.logger.error(f"Transformation error: {e}")
                    result.failed_records += 1
                    self._handle_failed_record(
                        record, 
                        ValidationResult(is_valid=False, record=record, errors=[str(e)]),
                        result
                    )
                    
                    if self._should_stop(result):
                        break
                    
                    continue
                
                # Load
                try:
                    if self.loader.load(transformed_record):
                        result.successful_records += 1
                    else:
                        result.failed_records += 1
                        self._handle_failed_record(
                            transformed_record,
                            ValidationResult(
                                is_valid=False, 
                                record=transformed_record, 
                                errors=["Load failed"]
                            ),
                            result
                        )
                except Exception as e:
                    self.logger.error(f"Load error: {e}")
                    result.failed_records += 1
                    result.errors.append(f"Load error: {e}")
                    
                    if self._should_stop(result):
                        break
            
            result.completed_at = datetime.utcnow()
            self.logger.info(f"Pipeline completed: {result.successful_records}/{result.total_records} successful")
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            result.errors.append(f"Pipeline error: {e}")
            result.completed_at = datetime.utcnow()
        
        return result
    
    def _validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        """Run all validators on a record."""
        all_errors = []
        all_warnings = []
        
        for validator in self.validators:
            result = validator.validate(record)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            
            if not result.is_valid and self.config.stop_on_error:
                break
        
        is_valid = len(all_errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            record=record,
            errors=all_errors,
            warnings=all_warnings
        )
    
    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all transformers to a record."""
        result = record
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result
    
    def _handle_failed_record(
        self, 
        record: Dict[str, Any], 
        validation_result: ValidationResult,
        pipeline_result: PipelineResult
    ):
        """Handle a failed record."""
        if self.buffer:
            try:
                quarantine_id = self.buffer.quarantine(record, validation_result.errors)
                pipeline_result.quarantined_records += 1
                self.logger.debug(f"Record quarantined: {quarantine_id}")
            except Exception as e:
                self.logger.error(f"Failed to quarantine record: {e}")
                pipeline_result.errors.append(f"Quarantine error: {e}")
        else:
            # Log errors if no buffer
            for error in validation_result.errors:
                self.logger.warning(f"Validation error: {error}")
    
    def _should_stop(self, result: PipelineResult) -> bool:
        """Check if pipeline should stop."""
        if self.config.stop_on_error:
            return True
        
        if self.config.max_errors and result.failed_records >= self.config.max_errors:
            self.logger.warning(f"Max errors reached: {self.config.max_errors}")
            return True
        
        return False
    
    def retry_quarantined(self, max_retries: Optional[int] = None) -> PipelineResult:
        """
        Retry quarantined records.
        
        Args:
            max_retries: Maximum retries per record (uses config if None)
            
        Returns:
            PipelineResult with retry statistics
        """
        if not self.buffer:
            raise ValueError("Buffer not configured for this pipeline")
        
        max_retries = max_retries or self.config.max_retries
        result = PipelineResult(started_at=datetime.utcnow())
        
        quarantined = self.buffer.get_quarantined()
        self.logger.info(f"Retrying {len(quarantined)} quarantined records")
        
        for qr in quarantined:
            if qr.retry_count >= max_retries:
                self.logger.debug(f"Skipping record {qr.id}: max retries reached")
                continue
            
            result.total_records += 1
            
            # Validate again
            validation_result = self._validate_record(qr.record)
            
            if validation_result.is_valid:
                # Transform and load
                try:
                    transformed = self._transform_record(validation_result.record)
                    if self.loader.load(transformed):
                        result.successful_records += 1
                        self.buffer.release(qr.id)
                        self.logger.debug(f"Record {qr.id} successfully retried")
                    else:
                        result.failed_records += 1
                        self.buffer.update_retry(qr.id)
                except Exception as e:
                    self.logger.error(f"Retry error for record {qr.id}: {e}")
                    result.failed_records += 1
                    self.buffer.update_retry(qr.id)
            else:
                result.failed_records += 1
                self.buffer.update_retry(qr.id)
                self.logger.debug(f"Record {qr.id} still invalid after retry")
        
        result.completed_at = datetime.utcnow()
        self.logger.info(f"Retry completed: {result.successful_records}/{result.total_records} successful")
        
        return result

