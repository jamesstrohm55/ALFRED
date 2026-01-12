"""
Centralized logging configuration for A.L.F.R.E.D.

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.exception("Exception with traceback")
"""
import logging
import os
from datetime import datetime
from pathlib import Path


# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file with date
LOG_FILE = LOG_DIR / f"alfred_{datetime.now().strftime('%Y%m%d')}.log"

# Configure root logger
_root_logger_configured = False


def _configure_root_logger():
    """Configure the root logger with file and console handlers."""
    global _root_logger_configured
    if _root_logger_configured:
        return

    root_logger = logging.getLogger("alfred")
    root_logger.setLevel(logging.DEBUG)

    # File handler - detailed logging
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler - less verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(levelname)-8s | %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    _root_logger_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance configured with file and console handlers
    """
    _configure_root_logger()

    # Create child logger under "alfred" namespace
    if name.startswith("alfred."):
        logger_name = name
    else:
        # Convert module path to logger name
        logger_name = f"alfred.{name.replace('__', '').strip('_')}"

    return logging.getLogger(logger_name)


# Convenience function for quick logging
def log_error(message: str, exc: Exception = None):
    """Quick error logging with optional exception."""
    logger = get_logger("quick")
    if exc:
        logger.error(f"{message}: {exc}", exc_info=True)
    else:
        logger.error(message)


def log_warning(message: str):
    """Quick warning logging."""
    logger = get_logger("quick")
    logger.warning(message)


def log_info(message: str):
    """Quick info logging."""
    logger = get_logger("quick")
    logger.info(message)
