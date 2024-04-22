import logging
import os

# Set up logging level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Create console handler and set level
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)
