"""File-based extractors for CSV, JSON, and other formats."""

import csv
import json
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List
import logging

from ..core import Extractor


logger = logging.getLogger(__name__)


class CSVExtractor(Extractor):
    """
    Extracts data from CSV files.
    
    Config options:
        - file_path: str - path to CSV file
        - delimiter: str - CSV delimiter (default: ',')
        - encoding: str - file encoding (default: 'utf-8')
        - skip_header: bool - whether to skip first row (default: False)
        - fieldnames: List[str] - custom field names (if None, uses first row)
    """
    
    def __init__(
        self,
        file_path: str,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        skip_header: bool = False,
        fieldnames: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize CSV extractor.
        
        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter
            encoding: File encoding
            skip_header: Whether to skip first row
            fieldnames: Custom field names
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.delimiter = delimiter
        self.encoding = encoding
        self.skip_header = skip_header
        self.fieldnames = fieldnames
        self._file_handle = None
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extract records from CSV file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        
        logger.info(f"Extracting from CSV: {self.file_path}")
        
        with open(self.file_path, 'r', encoding=self.encoding, newline='') as f:
            if self.fieldnames:
                reader = csv.DictReader(f, fieldnames=self.fieldnames, delimiter=self.delimiter)
                if self.skip_header:
                    next(reader)  # Skip header row
            else:
                reader = csv.DictReader(f, delimiter=self.delimiter)
            
            for row_num, row in enumerate(reader, start=1):
                # Convert OrderedDict to regular dict and strip whitespace
                record = {k.strip() if k else f'col_{i}': v.strip() if isinstance(v, str) else v 
                         for i, (k, v) in enumerate(row.items())}
                
                # Add metadata
                record['_source_line'] = row_num
                record['_source_file'] = str(self.file_path)
                
                yield record


class JSONExtractor(Extractor):
    """
    Extracts data from JSON files.
    
    Config options:
        - file_path: str - path to JSON file
        - json_path: str - path to records in JSON (e.g., 'data.records')
        - encoding: str - file encoding (default: 'utf-8')
    """
    
    def __init__(
        self,
        file_path: str,
        json_path: Optional[str] = None,
        encoding: str = 'utf-8',
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize JSON extractor.
        
        Args:
            file_path: Path to JSON file
            json_path: Path to records in JSON structure (dot notation)
            encoding: File encoding
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.json_path = json_path
        self.encoding = encoding
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extract records from JSON file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")
        
        logger.info(f"Extracting from JSON: {self.file_path}")
        
        with open(self.file_path, 'r', encoding=self.encoding) as f:
            data = json.load(f)
        
        # Navigate to records using json_path if provided
        if self.json_path:
            for key in self.json_path.split('.'):
                data = data.get(key, [])
        
        # Handle both single record and array of records
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError(f"JSON data must be an array or object, got {type(data)}")
        
        for idx, record in enumerate(data):
            if not isinstance(record, dict):
                logger.warning(f"Skipping non-dict record at index {idx}")
                continue
            
            # Add metadata
            record['_source_index'] = idx
            record['_source_file'] = str(self.file_path)
            
            yield record


class JSONLinesExtractor(Extractor):
    """
    Extracts data from JSON Lines files (.jsonl).
    
    Each line is a separate JSON object.
    
    Config options:
        - file_path: str - path to JSONL file
        - encoding: str - file encoding (default: 'utf-8')
        - skip_errors: bool - whether to skip invalid JSON lines (default: False)
    """
    
    def __init__(
        self,
        file_path: str,
        encoding: str = 'utf-8',
        skip_errors: bool = False,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize JSON Lines extractor.
        
        Args:
            file_path: Path to JSONL file
            encoding: File encoding
            skip_errors: Whether to skip invalid JSON lines
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.skip_errors = skip_errors
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extract records from JSON Lines file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {self.file_path}")
        
        logger.info(f"Extracting from JSONL: {self.file_path}")
        
        with open(self.file_path, 'r', encoding=self.encoding) as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        if self.skip_errors:
                            logger.warning(f"Skipping non-dict record at line {line_num}")
                            continue
                        else:
                            raise ValueError(f"Line {line_num}: Expected dict, got {type(record)}")
                    
                    # Add metadata
                    record['_source_line'] = line_num
                    record['_source_file'] = str(self.file_path)
                    
                    yield record
                    
                except json.JSONDecodeError as e:
                    if self.skip_errors:
                        logger.warning(f"Skipping invalid JSON at line {line_num}: {e}")
                        continue
                    else:
                        raise ValueError(f"Line {line_num}: Invalid JSON - {e}")


class FileExtractor(Extractor):
    """
    Auto-detecting file extractor that selects appropriate extractor based on file extension.
    """
    
    EXTRACTORS = {
        '.csv': CSVExtractor,
        '.json': JSONExtractor,
        '.jsonl': JSONLinesExtractor,
        '.ndjson': JSONLinesExtractor,
    }
    
    def __init__(self, file_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize file extractor.
        
        Args:
            file_path: Path to file
            config: Configuration to pass to specific extractor
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        
        # Detect file type and create appropriate extractor
        ext = self.file_path.suffix.lower()
        if ext not in self.EXTRACTORS:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported types: {', '.join(self.EXTRACTORS.keys())}"
            )
        
        extractor_class = self.EXTRACTORS[ext]
        self.extractor = extractor_class(file_path=str(file_path), **(config or {}))
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extract records using appropriate extractor."""
        return self.extractor.extract()

