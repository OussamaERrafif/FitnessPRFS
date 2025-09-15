"""
Logging utilities and decorators for services.

This module provides decorators and utilities that services can use
to automatically log operations, errors, and performance metrics.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional

from app.config.logging_config import (
    get_logger, 
    log_service_operation, 
    log_error, 
    log_performance,
    log_database_operation
)


def log_service_method(service_name: str, operation_name: str = None):
    """
    Decorator to automatically log service method calls.
    
    Args:
        service_name: Name of the service
        operation_name: Optional custom operation name (defaults to method name)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            logger = get_logger(f"app.services.{service_name}")
            logger.info(f"Starting {service_name}.{op_name}")
            
            try:
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                log_performance(
                    operation=f"{service_name}.{op_name}",
                    duration=duration
                )
                
                logger.info(f"Completed {service_name}.{op_name} successfully")
                return result
                
            except Exception as e:
                log_error(e, {
                    "service": service_name,
                    "operation": op_name,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                logger.error(f"Failed {service_name}.{op_name}: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            logger = get_logger(f"app.services.{service_name}")
            logger.info(f"Starting {service_name}.{op_name}")
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                log_performance(
                    operation=f"{service_name}.{op_name}",
                    duration=duration
                )
                
                logger.info(f"Completed {service_name}.{op_name} successfully")
                return result
                
            except Exception as e:
                log_error(e, {
                    "service": service_name,
                    "operation": op_name,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                logger.error(f"Failed {service_name}.{op_name}: {str(e)}")
                raise
        
        # Return appropriate wrapper based on whether function is async
        if hasattr(func, '__await__') or hasattr(func, '__aenter__'):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_database_method(table_name: str, operation: str = None):
    """
    Decorator to log database operations.
    
    Args:
        table_name: Name of the database table
        operation: Database operation type (create, read, update, delete)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            op = operation or func.__name__
            start_time = time.time()
            
            logger = get_logger("app.database")
            logger.debug(f"Database operation: {op} on {table_name}")
            
            try:
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                log_database_operation(op, table_name, {
                    "duration": duration,
                    "success": True
                })
                
                return result
                
            except Exception as e:
                log_database_operation(op, table_name, {
                    "error": str(e),
                    "success": False
                })
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            op = operation or func.__name__
            start_time = time.time()
            
            logger = get_logger("app.database")
            logger.debug(f"Database operation: {op} on {table_name}")
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                log_database_operation(op, table_name, {
                    "duration": duration,
                    "success": True
                })
                
                return result
                
            except Exception as e:
                log_database_operation(op, table_name, {
                    "error": str(e),
                    "success": False
                })
                raise
        
        # Return appropriate wrapper based on whether function is async
        if hasattr(func, '__await__') or hasattr(func, '__aenter__'):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ServiceLogger:
    """
    Logger class for services that provides convenient logging methods.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger(f"app.services.{service_name}")
    
    def info(self, message: str, **kwargs):
        """Log info message with service context."""
        self.logger.info(f"[{self.service_name}] {message}", extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with service context."""
        self.logger.warning(f"[{self.service_name}] {message}", extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with service context."""
        self.logger.error(f"[{self.service_name}] {message}", extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with service context."""
        self.logger.debug(f"[{self.service_name}] {message}", extra=kwargs)
    
    def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """Log a service operation."""
        log_service_operation(self.service_name, operation, details)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Log an error with additional context."""
        full_context = {"service": self.service_name}
        if context:
            full_context.update(context)
        log_error(error, full_context)


# Convenience function to get a service logger
def get_service_logger(service_name: str) -> ServiceLogger:
    """
    Get a service logger instance.
    
    Args:
        service_name: Name of the service
        
    Returns:
        ServiceLogger instance
    """
    return ServiceLogger(service_name)
