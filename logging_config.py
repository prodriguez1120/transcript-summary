#!/usr/bin/env python3
"""
Centralized logging configuration for FlexXray Transcript Summarizer

This module provides consistent logging configuration across all modules:
- Configurable log levels
- Structured log formatting
- File and console handlers
- Performance logging capabilities
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

# Default logging configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_FILE = "flexxray.log"

# Performance logging configuration
PERFORMANCE_LOG_LEVEL = logging.DEBUG
PERFORMANCE_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

def setup_logger(
    name: str,
    log_level: Optional[int] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (defaults to DEFAULT_LOG_LEVEL)
        log_file: Log file path (defaults to DEFAULT_LOG_FILE)
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    logger.setLevel(log_level or DEFAULT_LOG_LEVEL)
    
    # Create formatters
    console_formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    file_formatter = logging.Formatter(PERFORMANCE_LOG_FORMAT)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        # Ensure log directory exists
        log_file = log_file or DEFAULT_LOG_FILE
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_performance_logger(name: str) -> logging.Logger:
    """
    Get a logger specifically for performance logging.
    
    Args:
        name: Logger name
        
    Returns:
        Performance logger instance
    """
    logger = setup_logger(
        name,
        log_level=PERFORMANCE_LOG_LEVEL,
        log_file="flexxray_performance.log",
        enable_console=False,
        enable_file=True
    )
    return logger

def setup_root_logging(
    log_level: Optional[int] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Set up root logging configuration.
    
    Args:
        log_level: Root logging level
        log_file: Root log file path
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level or DEFAULT_LOG_LEVEL)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up root logger
    setup_logger(
        "root",
        log_level=log_level,
        log_file=log_file,
        enable_console=True,
        enable_file=True
    )

# Convenience functions for common logging patterns
def log_function_entry(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """Log function entry with parameters."""
    logger.debug(f"Entering {func_name} with params: {kwargs}")

def log_function_exit(logger: logging.Logger, func_name: str, result: any = None) -> None:
    """Log function exit with result."""
    logger.debug(f"Exiting {func_name} with result: {result}")

def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs) -> None:
    """Log performance metrics."""
    logger.info(f"Performance: {operation} took {duration:.3f}s - {kwargs}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str, **kwargs) -> None:
    """Log error with context information."""
    logger.error(f"Error in {context}: {error} - Context: {kwargs}")

# Initialize default logging
if __name__ == "__main__":
    setup_root_logging()
    logger = setup_logger(__name__)
    logger.info("Logging configuration initialized")
