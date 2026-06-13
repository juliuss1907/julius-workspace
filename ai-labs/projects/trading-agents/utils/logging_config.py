"""
Logging Configuration
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # System log file (rotating)
    system_handler = RotatingFileHandler(
        log_dir / "system.log",
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=3
    )
    system_handler.setLevel(log_level)
    system_handler.setFormatter(formatter)
    root_logger.addHandler(system_handler)
    
    # Errors log file
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    return root_logger


def get_logger(name: str):
    """Get logger for module"""
    return logging.getLogger(name)
