"""Logging configuration for Vibe-Code Auditor."""

import logging
import sys
from typing import Optional
from rich.logging import RichHandler


def setup_logger(
    name: str,
    level: str = "INFO",
    use_rich: bool = True
) -> logging.Logger:
    """
    Set up a logger with Rich formatting support.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_rich: Whether to use Rich formatting

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Starting analysis...")
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    if use_rich:
        # Rich handler for beautiful console output
        handler = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
            show_path=False
        )
    else:
        # Standard stream handler
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get an existing logger or create a new one.

    Args:
        name: Logger name
        level: Optional logging level override

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    if level:
        logger.setLevel(getattr(logging, level.upper()))

    return logger


# Module-level logger for utility functions
logger = setup_logger(__name__)
