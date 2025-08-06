"""
Logging utilities for the application.
"""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: Optional[str] = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create console handler if not already exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


# Application logger
app_logger = setup_logger("fastapi_app")

# Default logger export for convenience
logger = app_logger