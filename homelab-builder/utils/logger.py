#!/usr/bin/env python3
"""
Logger Setup
Configures logging for the homelab builder.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from rich.logging import RichHandler


def setup_logger(name: str = "homelab_builder", level: str = "INFO") -> logging.Logger:
    """Setup and configure logger with Rich handler."""
    
    # Create logs directory
    log_dir = Path("/opt/homelab/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with Rich
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=True
    )
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_format)
    
    # File handler
    log_file = log_dir / f"homelab_builder_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"homelab_builder.{name}")


# Create default logger
default_logger = setup_logger()
