"""
CyberVerdict Configuration Module

Defines global constants and logging configurations for the Deterministic Analysis Engine.
This module must not contain any business, parsing, or validation logic.
"""

import logging
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs"
DEFAULT_TEMP_DIR = BASE_DIR / "temp"
DEFAULT_SAMPLES_DIR = BASE_DIR / "samples"

# Ensure output and temp directories exist
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_TEMP_DIR.mkdir(parents=True, exist_ok=True)

# External tool paths (configurable via environment variables)
JADX_PATH = Path(os.getenv("CYBERVERDICT_JADX_PATH", "jadx"))
ADB_PATH = Path(os.getenv("CYBERVERDICT_ADB_PATH", "adb"))

# Hashing configurations
CANONICAL_HASH_ALGORITHM = "sha256"

# Timeout values (in seconds)
DEFAULT_TIMEOUT_SEC = 30.0

# Logging configurations
LOG_LEVEL = os.getenv("CYBERVERDICT_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
LOG_FILE = BASE_DIR / "analysis_engine.log"

def setup_logging(level: str | None = None) -> None:
    """
    Configures the global logging settings with console and file output handlers.
    
    Args:
        level (str | None): Optional logging level override (e.g. 'DEBUG', 'INFO', 'WARNING').
                            If not provided, the default LOG_LEVEL is used.
    """
    log_level_str = level or LOG_LEVEL
    numeric_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    stream_handler = logging.StreamHandler()
    
    # Configure formatter
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers to prevent duplicate formatting or destinations
    if root_logger.handlers:
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
