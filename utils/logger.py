"""
Logging configuration for TripGenie
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> None:
    """
    Configure logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
    """
    
    # Create log directory if needed
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler (colored output for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (detailed logs)
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d")
        file_handler = logging.FileHandler(
            f"{log_dir}/tripgenie_{timestamp}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    
    logger.info("=" * 80)
    logger.info("TripGenie Logging Initialized")
    logger.info("=" * 80)


def get_logger(name: str) -> 'TripGenieLogger':
    """
    Get a logger instance with custom methods
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        TripGenieLogger instance
    """
    return TripGenieLogger(name)


class TripGenieLogger:
    """Custom logger wrapper with context-aware methods"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, msg: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(msg, kwargs))
    
    def debug(self, msg: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(msg, kwargs))
    
    def warning(self, msg: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(msg, kwargs))
    
    def error(self, msg: str, exc: Optional[Exception] = None, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(msg, kwargs), exc_info=exc)
    
    def log_user_action(self, action: str, **kwargs):
        """Log user actions with context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.info(f"USER_ACTION: {action} | {context}")
    
    def log_api_call(self, api_name: str, status: str, duration: Optional[float] = None, **kwargs):
        """Log API calls"""
        msg = f"API_CALL: {api_name} | Status: {status}"
        if duration:
            msg += f" | Duration: {duration:.2f}s"
        if kwargs:
            msg += f" | {kwargs}"
        self.logger.info(msg)
    
    def log_search(self, query: str, results_count: int, duration: float):
        """Log search operations"""
        self.logger.info(
            f"SEARCH: Query='{query[:50]}' | Results={results_count} | Duration={duration:.2f}s"
        )
    
    def log_trip_generation(self, from_city: str, to_city: str, days: int, status: str, duration: Optional[float] = None):
        """Log trip generation"""
        msg = f"TRIP_GEN: {from_city} → {to_city} | {days} days | Status={status}"
        if duration:
            msg += f" | Duration={duration:.2f}s"
        self.logger.info(msg)
    
    def _format_message(self, msg: str, kwargs: dict) -> str:
        """Format message with additional context"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{msg} | {context}"
        return msg
