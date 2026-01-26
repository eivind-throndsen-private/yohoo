#!/usr/bin/env python3
"""
Shared logging configuration for all Yohoo scripts
Provides consistent logging setup with file and console handlers
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logging(
    script_name: str,
    log_level: str = "INFO",
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Set up logging with both file and console handlers.
    
    Args:
        script_name: Name of the script (used for log filename)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: logs/)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(script_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler - always detailed, always INFO or higher
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f"{script_name}_{timestamp}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler - respects log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Use simple format for INFO and above, detailed for DEBUG
    if log_level.upper() == 'DEBUG':
        console_handler.setFormatter(detailed_formatter)
    else:
        console_handler.setFormatter(simple_formatter)
    
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    
    return logger


def add_logging_arguments(parser) -> None:
    """
    Add standard logging arguments to an ArgumentParser.
    
    Args:
        parser: argparse.ArgumentParser instance
    """
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        '--verbose', '-v',
        action='store_const',
        const='INFO',
        dest='log_level',
        help='Enable verbose logging (INFO level)'
    )
    log_group.add_argument(
        '--debug',
        action='store_const',
        const='DEBUG',
        dest='log_level',
        help='Enable debug logging (DEBUG level)'
    )
    log_group.add_argument(
        '--quiet', '-q',
        action='store_const',
        const='ERROR',
        dest='log_level',
        help='Quiet mode - only show errors'
    )
    
    # Set default
    parser.set_defaults(log_level='WARNING')
