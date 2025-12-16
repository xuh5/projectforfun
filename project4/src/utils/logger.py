"""Logging configuration utilities."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = 'INFO',
    format: Optional[str] = None,
    log_file: Optional[str] = None
):
    """
    Setup logging configuration.
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        format: Log format string (uses default if None)
        log_file: Optional file path for log output
    """
    if format is None:
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(format)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=format,
        handlers=handlers
    )
    
    logging.info(f"Logging configured: level={level}")

