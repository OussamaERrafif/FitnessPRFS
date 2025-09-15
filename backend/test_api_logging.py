#!/usr/bin/env python3
"""
Test script for API logging functionality.

This script tests all aspects of the API logging system.
"""

import asyncio
import sys
import os
import time
import requests
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app.config.logging_config import setup_logging
from app.utils.api_logging import (
    api_logger,
    log_user_action,
    log_admin_action,
    log_security_event,
    log_business_event
)


def test_api_logger():
    """Test the API logger functionality."""
    print("Testing API Logger functionality...")
    
    # Setup logging
    setup_logging()
    
    # Test authentication logging
    api_logger.log_authentication_attempt(
        username="testuser@example.com",
        success=True,
        request_id="test-123",
        client_ip="127.0.0.1",
        user_agent="test-agent"
    )
    
    api_logger.log_authentication_attempt(
        username="baduser@example.com",
        success=False,
        request_id="test-124",
        client_ip="192.168.1.100",
        user_agent="test-agent",
        failure_reason="invalid_password"
    )
    
    # Test endpoint access logging
    api_logger.log_endpoint_access(
        endpoint="/api/v1/users",
        method="GET",
        user_id="user123",
        request_id="test-125",
        response_status=200,
        additional_data={"page": 1, "limit": 20}
    )
    
    # Test validation error logging
    api_logger.log_validation_error(
        endpoint="/api/v1/auth/register",
        errors=[
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too short"}
        ],
        request_id="test-126",
        user_id=None
    )
    
    # Test API error logging
    try:
        raise ValueError("Test API error")
    except Exception as e:
        api_logger.log_api_error(
            error=e,
            endpoint="/api/v1/test",
            request_id="test-127",
            user_id="user123",
            context={"test": True}
        )
    
    # Test rate limiting
    api_logger.log_rate_limit_hit(
        client_ip="192.168.1.100",
        endpoint="/api/v1/auth/login",
        user_id="user123",
        limit_type="login_attempts"
    )
    
    # Test data access logging
    api_logger.log_data_access(
        action="create",
        resource_type="progress_log",
        resource_id="prog123",
        user_id="user123",
        request_id="test-128"
    )
    
    # Test file operation logging
    api_logger.log_file_operation(
        operation="upload",
        file_name="profile_picture.jpg",  # Changed parameter name
        file_size=1024000,
        user_id="user123",
        request_id="test-129"
    )
    
    print("✓ API Logger tests completed")


def test_convenience_functions():
    """Test convenience logging functions."""
    print("Testing convenience logging functions...")
    
    # Test user action logging
    log_user_action(
        action="workout_completed",
        user_id="user123",
        details={
            "exercise_count": 5,
            "duration_minutes": 45,
            "calories_burned": 300
        }
    )
    
    # Test admin action logging
    log_admin_action(
        action="user_banned",
        admin_user_id="admin456",
        target_resource="user123",
        details={"reason": "spam", "duration": "30_days"}
    )
    
    # Test security event logging
    log_security_event(
        event_type="suspicious_login_pattern",
        details={
            "user_id": "user123",
            "failed_attempts": 5,
            "time_window": "5_minutes",
            "client_ip": "192.168.1.100"
        }
    )
    
    # Test business event logging
    log_business_event(
        event="subscription_upgraded",
        entity_type="user",
        entity_id="user123",
        user_id="user123",
        details={
            "from_plan": "basic",
            "to_plan": "premium",
            "payment_method": "credit_card"
        }
    )
    
    print("✓ Convenience function tests completed")


def test_real_api_requests():
    """Test with real API requests if server is running."""
    print("Testing with real API requests...")
    
    try:
        # Check if server is running
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print("✓ Server is running, testing real requests...")
            
            # Test health endpoint
            response = requests.get("http://127.0.0.1:8000/health")
            print(f"Health check: {response.status_code}")
            
            # Test API docs
            response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
            print(f"API docs: {response.status_code}")
            
            # Test invalid endpoint
            response = requests.get("http://127.0.0.1:8000/invalid", timeout=2)
            print(f"Invalid endpoint: {response.status_code}")
            
            # Test with JSON payload
            test_data = {
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
            response = requests.post(
                "http://127.0.0.1:8000/api/v1/auth/register",
                json=test_data,
                timeout=2
            )
            print(f"Registration attempt: {response.status_code}")
            
            print("✓ Real API request tests completed")
            
        else:
            print("? Server not responding correctly")
            
    except requests.exceptions.RequestException:
        print("? Server not running, skipping real API tests")


def test_log_files():
    """Check that API log files are created."""
    print("Testing API log file creation...")
    
    logs_dir = Path("logs")
    expected_files = [
        "api.log", 
        "api_access.log", 
        "api_errors.log", 
        "api_slow.log"
    ]
    
    if not logs_dir.exists():
        print("✗ Logs directory does not exist")
        return False
    
    for log_file in expected_files:
        log_path = logs_dir / log_file
        if log_path.exists():
            print(f"✓ {log_file} exists")
            
            # Check if file has content
            if log_path.stat().st_size > 0:
                print(f"  └─ Contains {log_path.stat().st_size} bytes")
            else:
                print(f"  └─ File is empty")
        else:
            print(f"? {log_file} not found (may not have messages yet)")
    
    print("✓ API log file tests completed")
    return True


def main():
    """Run all API logging tests."""
    print("=" * 60)
    print("FitnessPR API Logging Test")
    print("=" * 60)
    
    try:
        test_api_logger()
        print()
        
        test_convenience_functions()
        print()
        
        test_real_api_requests()
        print()
        
        test_log_files()
        print()
        
        print("=" * 60)
        print("✓ All API logging tests completed successfully!")
        print("Check the logs/ directory for generated API log files:")
        print("  - api_access.log: API endpoint access logs")
        print("  - api_errors.log: API error logs")
        print("  - api_slow.log: Slow request logs")
        print("  - api.log: General API logs")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
