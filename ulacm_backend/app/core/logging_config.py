# File: ulacm_backend/app/core/logging_config.py
# Purpose: Configures logging for the application.

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from app.core.config import settings # To potentially use settings for log level/file

def setup_logging():
    """
    Configures logging to output to console (stdout) with a specific format.
    Complies with NFR-AVAIL-004.
    """
    log_level_str = getattr(settings, "LOG_LEVEL", "INFO").upper() # Default to INFO if not set
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Define log format
    log_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z" # ISO 8601 like format with timezone
    )

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates if setup is called again
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler (stdout) - suitable for Docker logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(log_level)

    # Add console handler to the root logger
    root_logger.addHandler(console_handler)

    # --- Optional: File Handler (Example) ---
    # If file logging is desired in addition to console:
    # log_file = getattr(settings, "LOG_FILE_PATH", None)
    # if log_file:
    #     file_handler = TimedRotatingFileHandler(
    #         log_file, when="midnight", interval=1, backupCount=7, encoding='utf-8'
    #     )
    #     file_handler.setFormatter(log_formatter)
    #     file_handler.setLevel(log_level)
    #     root_logger.addHandler(file_handler)
    # -----------------------------------------

    # Set higher level for noisy libraries if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # !!! TODO: Change in PRODUCTION !!!
    logging.getLogger("app.crud").setLevel(logging.DEBUG)

    logging.info(f"Logging configured with level: {log_level_str}")

# --- Initial setup call ---
# setup_logging() # Call this early, e.g., in main.py
# For now, define the function here and call it from main.py
