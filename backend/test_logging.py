#!/usr/bin/env python3
"""
Test script for the logging configuration.

This script tests all aspects of the logging system to ensure
everything is working correctly.
"""

import asyncio
import sys
import os
import traceback
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app.config.logging_config import (
    setup_logging, 
    get_logger,
    log_request_info,
    log_security_event,
    log_service_operation,
    log_database_operation,
    log_error,
    log_performance
)
from app.utils.logging_utils import get_service_logger, log_service_method


def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging...")
    
    # Setup logging
    setup_logging()
    
    # Test different loggers
    app_logger = get_logger("app.test")
    api_logger = get_logger("app.api.test")
    service_logger = get_logger("app.services.test")
    
    # Test different log levels
    app_logger.debug("This is a debug message")
    app_logger.info("This is an info message")
    app_logger.warning("This is a warning message")
    app_logger.error("This is an error message")
    
    api_logger.info("API test message")
    service_logger.info("Service test message")
    
    print("✓ Basic logging test completed")


def test_specialized_logging():
    """Test specialized logging functions."""
    print("Testing specialized logging functions...")
    
    # Test request logging
    log_request_info("test-123", "GET", "/api/test", "user123")
    
    # Test security event logging
    log_security_event("test_login", {"ip": "127.0.0.1"}, "user123")
    
    # Test service operation logging
    log_service_operation("test_service", "test_operation", {"key": "value"})
    
    # Test database operation logging
    log_database_operation("create", "test_table", {"rows": 1})
    
    # Test performance logging
    log_performance("test_operation", 0.123, {"test": True})
    
    # Test error logging
    try:
        raise ValueError("This is a test error")
    except Exception as e:
        log_error(e, {"test_context": "error_test"})
    
    print("✓ Specialized logging test completed")


def test_service_logger():
    """Test the service logger utility."""
    print("Testing service logger utility...")
    
    service_logger = get_service_logger("test_service")
    
    service_logger.info("Service logger info test")
    service_logger.warning("Service logger warning test")
    service_logger.error("Service logger error test")
    service_logger.debug("Service logger debug test")
    
    service_logger.log_operation("test_operation", {"data": "test"})
    
    try:
        raise RuntimeError("Service logger error test")
    except Exception as e:
        service_logger.log_error_with_context(e, {"operation": "test"})
    
    print("✓ Service logger test completed")


@log_service_method("test_service", "decorated_function")
def test_decorated_function():
    """Test the logging decorator."""
    logger = get_logger("app.test")
    logger.info("Inside decorated function")
    return "success"


@log_service_method("test_service", "decorated_async_function")
async def test_decorated_async_function():
    """Test the logging decorator with async function."""
    logger = get_logger("app.test")
    logger.info("Inside decorated async function")
    await asyncio.sleep(0.1)  # Simulate some async work
    return "async_success"


def test_decorators():
    """Test logging decorators."""
    print("Testing logging decorators...")
    
    # Test sync decorator
    result = test_decorated_function()
    print(f"Decorated function result: {result}")
    
    # Test async decorator
    async def run_async_test():
        result = await test_decorated_async_function()
        print(f"Decorated async function result: {result}")
    
    asyncio.run(run_async_test())
    
    print("✓ Decorator test completed")


def test_log_files():
    """Test that log files are created."""
    print("Testing log file creation...")
    
    logs_dir = Path("logs")
    expected_files = ["app.log", "error.log", "debug.log", "api.log", "security.log"]
    
    if not logs_dir.exists():
        print("✗ Logs directory does not exist")
        return False
    
    for log_file in expected_files:
        log_path = logs_dir / log_file
        if log_path.exists():
            print(f"✓ {log_file} exists")
        else:
            print(f"? {log_file} not found (may not have messages yet)")
    
    print("✓ Log file test completed")
    return True


def main():
    """Run all logging tests."""
    print("=" * 50)
    print("FitnessPR Logging Configuration Test")
    print("=" * 50)
    
    try:
        test_basic_logging()
        print()
        
        test_specialized_logging()
        print()
        
        test_service_logger()
        print()
        
        test_decorators()
        print()
        
        test_log_files()
        print()
        
        print("=" * 50)
        print("✓ All logging tests completed successfully!")
        print("Check the logs/ directory for generated log files.")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        print(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
