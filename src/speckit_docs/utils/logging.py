"""Logging configuration for speckit-docs."""

import logging
import sys
from typing import Any


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging for speckit-docs.

    Args:
        verbose: Enable DEBUG level logging
        quiet: Enable ERROR level logging only

    Raises:
        ValueError: If both verbose and quiet are True
    """
    if verbose and quiet:
        raise ValueError("Cannot set both verbose and quiet flags")

    # Determine log level
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout,
        force=True,  # Override any existing configuration
    )

    # Suppress verbose logging from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("git").setLevel(logging.WARNING)
    logging.getLogger("jinja2").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_info(message: str, **kwargs: Any) -> None:
    """Log an INFO level message.

    Args:
        message: Log message
        **kwargs: Additional context to include in the log
    """
    logger = get_logger(__name__)
    if kwargs:
        logger.info(f"{message} | {kwargs}")
    else:
        logger.info(message)


def log_debug(message: str, **kwargs: Any) -> None:
    """Log a DEBUG level message.

    Args:
        message: Log message
        **kwargs: Additional context to include in the log
    """
    logger = get_logger(__name__)
    if kwargs:
        logger.debug(f"{message} | {kwargs}")
    else:
        logger.debug(message)


def log_error(message: str, **kwargs: Any) -> None:
    """Log an ERROR level message.

    Args:
        message: Log message
        **kwargs: Additional context to include in the log
    """
    logger = get_logger(__name__)
    if kwargs:
        logger.error(f"{message} | {kwargs}")
    else:
        logger.error(message)


def log_warning(message: str, **kwargs: Any) -> None:
    """Log a WARNING level message.

    Args:
        message: Log message
        **kwargs: Additional context to include in the log
    """
    logger = get_logger(__name__)
    if kwargs:
        logger.warning(f"{message} | {kwargs}")
    else:
        logger.warning(message)
