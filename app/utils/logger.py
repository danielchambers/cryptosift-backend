"""
logger.debug(), logger.info(), logger.warning(), logger.error(), and logger.critical()
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Set up logging level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Create console handler and set level
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

# Create file handler and set level
file_handler = RotatingFileHandler("app.log", maxBytes=10485760, backupCount=10)
file_handler.setLevel(LOG_LEVEL)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)

# Add formatter to handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
