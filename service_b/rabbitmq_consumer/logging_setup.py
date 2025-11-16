import logging.config
import os
from logging_config import LOGGING_CONFIG, LOG_DIR  


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)