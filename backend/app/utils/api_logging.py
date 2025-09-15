"""
API-specific logging utilities for the FitnessPR API.

This module provides utilities for logging API-specific events such as:
- Authentication attempts
- API endpoint usage
- Rate limiting
- API errors and exceptions
- Data validation errors
"""

import json
import time
from typing import Any, Dict, Optional, List
from fastapi import Request, Response

from app.config.logging_config import get_logger


class APILogger:
    """Centralized API logging utility."""
    
    def __init__(self):
        self.request_logger = get_logger("app.api.requests")
        self.error_logger = get_logger("app.api.errors")
        self.auth_logger = get_logger("app.api.auth")
        self.validation_logger = get_logger("app.api.validation")
        self.access_logger = get_logger("app.api.access")
    
    def log_authentication_attempt(
        self, 
        username: str, 
        success: bool, 
        request_id: str,
        client_ip: str,
        user_agent: str = None,
        failure_reason: str = None
    ):
        """Log authentication attempts."""
        log_data = {
            "request_id": request_id,
            "username": username,
            "success": success,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": time.time()
        }
        
        if not success and failure_reason:
            log_data["failure_reason"] = failure_reason
        
        if success:
            self.auth_logger.info("Authentication successful", extra=log_data)
        else:
            self.auth_logger.warning("Authentication failed", extra=log_data)
    
    def log_endpoint_access(
        self,
        endpoint: str,
        method: str,
        user_id: str = None,
        request_id: str = None,
        response_status: int = None,
        additional_data: Dict[str, Any] = None
    ):
        """Log API endpoint access."""
        log_data = {
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "request_id": request_id,
            "response_status": response_status,
            "timestamp": time.time()
        }
        
        if additional_data:
            log_data.update(additional_data)
        
        self.access_logger.info("Endpoint accessed", extra=log_data)
    
    def log_validation_error(
        self,
        endpoint: str,
        errors: List[Dict[str, Any]],
        request_id: str = None,
        user_id: str = None
    ):
        """Log validation errors."""
        log_data = {
            "endpoint": endpoint,
            "validation_errors": errors,
            "request_id": request_id,
            "user_id": user_id,
            "timestamp": time.time()
        }
        
        self.validation_logger.warning("Validation error", extra=log_data)
    
    def log_api_error(
        self,
        error: Exception,
        endpoint: str,
        request_id: str = None,
        user_id: str = None,
        context: Dict[str, Any] = None
    ):
        """Log API errors with context."""
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "endpoint": endpoint,
            "request_id": request_id,
            "user_id": user_id,
            "timestamp": time.time()
        }
        
        if context:
            log_data["context"] = context
        
        self.error_logger.error("API error occurred", extra=log_data, exc_info=True)
    
    def log_rate_limit_hit(
        self,
        client_ip: str,
        endpoint: str,
        user_id: str = None,
        limit_type: str = "general"
    ):
        """Log rate limit violations."""
        log_data = {
            "client_ip": client_ip,
            "endpoint": endpoint,
            "user_id": user_id,
            "limit_type": limit_type,
            "timestamp": time.time()
        }
        
        self.error_logger.warning("Rate limit exceeded", extra=log_data)
    
    def log_data_access(
        self,
        action: str,  # 'create', 'read', 'update', 'delete'
        resource_type: str,  # 'user', 'exercise', 'progress_log', etc.
        resource_id: str = None,
        user_id: str = None,
        request_id: str = None,
        success: bool = True
    ):
        """Log data access operations."""
        log_data = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "request_id": request_id,
            "success": success,
            "timestamp": time.time()
        }
        
        self.access_logger.info(f"Data {action} operation", extra=log_data)
    
    def log_file_operation(
        self,
        operation: str,  # 'upload', 'download', 'delete'
        file_name: str,  # Changed from 'filename' to avoid conflict
        file_size: int = None,
        user_id: str = None,
        request_id: str = None,
        success: bool = True
    ):
        """Log file operations."""
        log_data = {
            "operation": operation,
            "file_name": file_name,  # Changed from 'filename'
            "file_size": file_size,
            "user_id": user_id,
            "request_id": request_id,
            "success": success,
            "timestamp": time.time()
        }
        
        self.access_logger.info(f"File {operation} operation", extra=log_data)


# Global API logger instance
api_logger = APILogger()


def log_api_call(func):
    """Decorator to automatically log API endpoint calls."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            api_logger.access_logger.info(
                f"API call completed: {func_name}",
                extra={
                    "function": func_name,
                    "duration": duration,
                    "success": True,
                    "timestamp": time.time()
                }
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            api_logger.error_logger.error(
                f"API call failed: {func_name}",
                extra={
                    "function": func_name,
                    "error": str(e),
                    "duration": duration,
                    "success": False,
                    "timestamp": time.time()
                },
                exc_info=True
            )
            raise
    
    return wrapper


def get_request_context(request: Request) -> Dict[str, Any]:
    """Extract logging context from FastAPI request."""
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "request_id": request.headers.get("x-request-id", "unknown")
    }


# Convenience functions for common logging patterns
def log_user_action(action: str, user_id: str, details: Dict[str, Any] = None):
    """Log user actions."""
    log_data = {
        "action": action,
        "user_id": user_id,
        "timestamp": time.time()
    }
    
    if details:
        log_data.update(details)
    
    api_logger.access_logger.info(f"User action: {action}", extra=log_data)


def log_admin_action(action: str, admin_user_id: str, target_resource: str = None, details: Dict[str, Any] = None):
    """Log administrative actions."""
    log_data = {
        "action": action,
        "admin_user_id": admin_user_id,
        "target_resource": target_resource,
        "timestamp": time.time()
    }
    
    if details:
        log_data.update(details)
    
    api_logger.access_logger.warning(f"Admin action: {action}", extra=log_data)


def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security-related events."""
    log_data = {
        "event_type": event_type,
        "timestamp": time.time()
    }
    log_data.update(details)
    
    api_logger.auth_logger.warning(f"Security event: {event_type}", extra=log_data)


def log_business_event(event: str, entity_type: str, entity_id: str = None, user_id: str = None, details: Dict[str, Any] = None):
    """Log business logic events."""
    log_data = {
        "event": event,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "user_id": user_id,
        "timestamp": time.time()
    }
    
    if details:
        log_data.update(details)
    
    api_logger.access_logger.info(f"Business event: {event}", extra=log_data)
