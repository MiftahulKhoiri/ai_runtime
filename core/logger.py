"""
logger.py
Unified logger untuk ai_factory & ai_runtime
"""

import logging
import os
from pathlib import Path

# ===============================
# KONFIG GLOBAL
# ===============================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.environ.get("LOG_TO_FILE", "0") == "1"

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


# ===============================
# LOGGER FACTORY
# ===============================
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # hindari duplicate handler

    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Optional file handler
    if LOG_TO_FILE:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger