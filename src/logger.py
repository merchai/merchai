import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

def get_logger(name: str) -> logging.Logger:
    # Create a logger with the name or use existing.
    logger = logging.getLogger(name)

    # Only setup the logger if it doesn't have a handler, prevent duplicate log messages.
    if not logger.handlers:

        # Handler sends logs to the console.
        handler = logging.StreamHandler()

        # Define how each log message should be formatted
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)

    return logger