"""File-based loaders for writing data to files."""

import csv
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from ..core import Loader


logger = logging.getLogger(__name__)


class CSVLoader(Loader):
    """
    Loads data to CSV files.
    
    Config options:
        - file_path: str - output CSV file path
        - fieldnames: List[str] - CSV column names (if None, inferred from first record)
        - delimiter: str - CSV delimiter (default: ',')
        - mode: str - file mode: 'w' (overwrite) or 'a' (append) (default: 'w')
    """
    
    def __init__(
        self,
        file_path: str,
        fieldnames: Optional[List[str]] = None,
        delimiter: str = ',',
        mode: str = 'w',
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize CSV loader.
        
        Args:
            file_path: Output CSV file path
            fieldnames: CSV column names
            delimiter: CSV delimiter
            mode: File mode ('w' or 'a')
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.fieldnames = fieldnames
        self.delimiter = delimiter
        self.mode = mode
        self._writer = None
        self._file_handle = None
        self._first_record = True
        
        # Create directory if needed
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file
        self._open()
    
    def _open(self):
        """Open the CSV file for writing."""
        self._file_handle = open(self.file_path, self.mode, newline='', encoding='utf-8')
        
        if self.fieldnames:
            self._writer = csv.DictWriter(
                self._file_handle,
                fieldnames=self.fieldnames,
                delimiter=self.delimiter
            )
            if self.mode == 'w':
                self._writer.writeheader()
    
    def load(self, record: Dict[str, Any]) -> bool:
        """Load a record to CSV."""
        try:
            # Infer fieldnames from first record if not provided
            if self._writer is None:
                self.fieldnames = list(record.keys())
                self._writer = csv.DictWriter(
                    self._file_handle,
                    fieldnames=self.fieldnames,
                    delimiter=self.delimiter
                )
                if self.mode == 'w':
                    self._writer.writeheader()
            
            # Write record
            self._writer.writerow(record)
            self._file_handle.flush()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write record to CSV: {e}")
            return False
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close file on exit."""
        if self._file_handle:
            self._file_handle.close()


class JSONLoader(Loader):
    """
    Loads data to JSON file (as array).
    
    Config options:
        - file_path: str - output JSON file path
        - indent: int - JSON indentation (default: 2)
    """
    
    def __init__(
        self,
        file_path: str,
        indent: int = 2,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize JSON loader.
        
        Args:
            file_path: Output JSON file path
            indent: JSON indentation
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.indent = indent
        self._records: List[Dict[str, Any]] = []
        
        # Create directory if needed
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self, record: Dict[str, Any]) -> bool:
        """Add record to buffer."""
        self._records.append(record)
        return True
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Write all records to file on exit."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self._records, f, indent=self.indent, ensure_ascii=False)
            logger.info(f"Wrote {len(self._records)} records to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to write JSON file: {e}")


class JSONLinesLoader(Loader):
    """
    Loads data to JSON Lines file (.jsonl).
    
    Each record is written as a separate JSON line.
    
    Config options:
        - file_path: str - output JSONL file path
        - mode: str - file mode: 'w' (overwrite) or 'a' (append) (default: 'w')
    """
    
    def __init__(
        self,
        file_path: str,
        mode: str = 'w',
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize JSON Lines loader.
        
        Args:
            file_path: Output JSONL file path
            mode: File mode ('w' or 'a')
            config: Additional configuration
        """
        super().__init__(config)
        self.file_path = Path(file_path)
        self.mode = mode
        self._file_handle = None
        
        # Create directory if needed
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file
        self._file_handle = open(self.file_path, mode, encoding='utf-8')
    
    def load(self, record: Dict[str, Any]) -> bool:
        """Write record as JSON line."""
        try:
            json_line = json.dumps(record, ensure_ascii=False)
            self._file_handle.write(json_line + '\n')
            self._file_handle.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to write record to JSONL: {e}")
            return False
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close file on exit."""
        if self._file_handle:
            self._file_handle.close()

