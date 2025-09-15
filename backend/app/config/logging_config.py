"""
Logging configuration module for FitnessPR API.

This module provides centralized logging configuration that:
- Logs everything to the /logs folder
- Provides different log levels and formats
- Includes rotating file handlers to manage log size
- Separates logs by type (app, api, security, debug, error)
"""

import logging
import logging.config
import os
import yaml
from pathlib import Path
from typing import Dict, Any

from app.config.config import settings


def setup_logging() -> None:
    """
    Setup logging configuration from YAML file.
    
    Creates the logs directory if it doesn't exist and configures
    all loggers according to the logging.yaml configuration.
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Load logging configuration
    config_path = Path("app/config/logging.yaml")
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Adjust log levels based on environment
        if settings.debug:
            # In debug mode, set more verbose logging
            config['root']['level'] = 'DEBUG'
            config['loggers']['app']['level'] = 'DEBUG'
            config['handlers']['console']['level'] = 'DEBUG'
        else:
            # In production, reduce console logging
            config['handlers']['console']['level'] = 'WARNING'
        
        # Configure logging
        logging.config.dictConfig(config)
        
        # Log that logging has been configured
        logger = logging.getLogger("app.config.logging")
        logger.info(f"Logging configured successfully. Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Logs directory: {logs_dir.absolute()}")
        
    else:
        # Fallback to basic configuration if YAML file not found
        logging.basicConfig(
            level=logging.DEBUG if settings.debug else logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(logs_dir / "app.log")
            ]
        )
        
        logger = logging.getLogger("app.config.logging")
        logger.warning(f"Logging YAML config not found at {config_path}. Using fallback configuration.")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name, typically __name__ from the calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request_info(request_id: str, method: str, url: str, user_id: str = None) -> None:
    """
    Log API request information.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method
        url: Request URL
        user_id: Optional user ID for the request
    """
    logger = get_logger("app.api.requests")
    logger.info(
        f"Request {request_id}: {method} {url}" + 
        (f" - User: {user_id}" if user_id else " - Anonymous")
    )


def log_security_event(event_type: str, details: Dict[str, Any], user_id: str = None) -> None:
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event (login, logout, failed_auth, etc.)
        details: Additional event details
        user_id: Optional user ID involved in the event
    """
    logger = get_logger("app.auth.security")
    logger.warning(
        f"Security Event: {event_type}" +
        (f" - User: {user_id}" if user_id else "") +
        f" - Details: {details}"
    )


def log_service_operation(service: str, operation: str, details: Dict[str, Any] = None) -> None:
    """
    Log service operation information.
    
    Args:
        service: Service name
        operation: Operation being performed
        details: Optional additional details
    """
    logger = get_logger(f"app.services.{service}")
    logger.info(
        f"Service Operation: {service}.{operation}" +
        (f" - Details: {details}" if details else "")
    )


def log_database_operation(operation: str, table: str, details: Dict[str, Any] = None) -> None:
    """
    Log database operation information.
    
    Args:
        operation: Database operation (create, read, update, delete)
        table: Database table name
        details: Optional additional details
    """
    logger = get_logger("app.database")
    logger.debug(
        f"Database Operation: {operation} on {table}" +
        (f" - Details: {details}" if details else "")
    )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log error information with context.
    
    Args:
        error: Exception that occurred
        context: Optional context information
    """
    logger = get_logger("app.errors")
    logger.error(
        f"Error: {type(error).__name__}: {str(error)}" +
        (f" - Context: {context}" if context else ""),
        exc_info=True
    )


# Application performance logging
def log_performance(operation: str, duration: float, details: Dict[str, Any] = None) -> None:
    """
    Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        details: Optional additional details
    """
    logger = get_logger("app.performance")
    logger.info(
        f"Performance: {operation} took {duration:.3f}s" +
        (f" - Details: {details}" if details else "")
    )
