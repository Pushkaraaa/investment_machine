"""
Logging configuration for the Investment Machine.
"""
import os
import sys
from pathlib import Path
from loguru import logger

from config.settings import LOG_LEVEL, BASE_DIR

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure Loguru logger
CONFIG = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "level": LOG_LEVEL,
        },
        {
            "sink": LOGS_DIR / "investment_machine.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "level": LOG_LEVEL,
            "rotation": "10 MB",
            "retention": "1 week",
            "compression": "zip",
        },
    ],
}

# Remove default logger and apply our configuration
logger.remove()
for handler in CONFIG["handlers"]:
    logger.add(**handler)

# Create specialized loggers
data_logger = logger.bind(category="data")
agent_logger = logger.bind(category="agent")
pipeline_logger = logger.bind(category="pipeline")
trading_logger = logger.bind(category="trading")

# Export the loggers
__all__ = ["logger", "data_logger", "agent_logger", "pipeline_logger", "trading_logger"] 