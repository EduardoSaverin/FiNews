import logging
import colorlog
import os
from datetime import datetime

# Directory 
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"finews_{datetime.now().strftime('%Y-%m-%d')}.log")

# Format
LOG_FORMAT = "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Color scheme
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

def setup_logger(name: str = "finews"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console handler with color
        console_handler = colorlog.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT, log_colors=LOG_COLORS)
        console_handler.setFormatter(console_formatter)

        # File handler (no colors)
        file_handler = logging.FileHandler(LOG_FILE)
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    # Capture all logs from third-party libraries (root logger)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # Remove default handlers if any
    root_logger.handlers.clear()
    # Add our handlers to root
    for handler in logger.handlers:
        root_logger.addHandler(handler)
    # Prevent propagation duplicates
    logger.propagate = False

    return logger

logger = setup_logger()