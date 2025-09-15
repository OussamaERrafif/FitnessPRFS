# FitnessPR Logging System

This document describes the comprehensive logging system implemented for the FitnessPR API backend.

## Overview

The logging system provides:
- **Global Configuration**: Centralized logging setup using YAML configuration
- **Multiple Log Files**: Separate logs for different types of events
- **Structured Logging**: Both human-readable and JSON formats
- **Automatic Rotation**: Log file rotation to manage disk space
- **Performance Tracking**: Built-in performance monitoring
- **Security Logging**: Dedicated security event tracking
- **Service Integration**: Easy-to-use decorators and utilities for services

## Log Files

All logs are stored in the `/logs` directory:

| File | Purpose | Format | Level |
|------|---------|--------|-------|
| `app.log` | General application logs | Detailed | INFO+ |
| `error.log` | Error logs only | Detailed | ERROR+ |
| `debug.log` | Debug information | Detailed | DEBUG+ |
| `api.log` | API requests and responses | JSON | INFO+ |
| `security.log` | Security events | Detailed | WARNING+ |

## Configuration

### YAML Configuration (`app/config/logging.yaml`)

The logging system uses a YAML configuration file that defines:
- **Formatters**: Different output formats (default, detailed, JSON)
- **Handlers**: File and console handlers with rotation
- **Loggers**: Specific loggers for different parts of the application
- **Levels**: Appropriate log levels for each component

### Environment-based Settings

The logging behavior changes based on the environment:

- **Development**: Debug level logging, verbose console output
- **Production**: Warning level console output, full file logging

## Usage

### Basic Logging

```python
from app.config.logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Service Logging

```python
from app.utils.logging_utils import get_service_logger, log_service_method

# Get a service-specific logger
service_logger = get_service_logger("user_service")

# Use the service logger
service_logger.info("User operation completed")
service_logger.log_operation("create_user", {"user_id": "123"})

# Use decorators for automatic logging
@log_service_method("user_service", "create_user")
def create_user(user_data):
    # Function automatically logged
    return create_user_logic(user_data)
```

### Security Event Logging

```python
from app.config.logging_config import log_security_event

# Log security events
log_security_event("login_attempt", {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
}, user_id="user123")

log_security_event("password_change", {
    "timestamp": datetime.utcnow().isoformat()
}, user_id="user123")
```

### Performance Logging

```python
from app.config.logging_config import log_performance

# Log performance metrics
log_performance("database_query", 0.150, {
    "query_type": "SELECT",
    "table": "users",
    "rows_returned": 25
})
```

### Database Operation Logging

```python
from app.config.logging_config import log_database_operation

# Log database operations
log_database_operation("create", "users", {
    "user_id": "123",
    "operation_success": True
})
```

### Error Logging with Context

```python
from app.config.logging_config import log_error

try:
    risky_operation()
except Exception as e:
    log_error(e, {
        "operation": "user_creation",
        "user_data": sanitized_user_data,
        "request_id": request_id
    })
```

## Request Logging

The system automatically logs all HTTP requests through middleware:

```json
{
  "timestamp": "2025-09-12 17:29:09",
  "logger": "app.api.requests",
  "level": "INFO",
  "module": "main",
  "function": "log_requests",
  "line": 42,
  "message": "Request abc-123: GET /api/users/123 - User: user456"
}
```

Each request includes:
- Unique request ID
- HTTP method and URL
- User ID (if authenticated)
- Response time and status code
- Client IP address

## Log Rotation

All log files use rotating file handlers:
- **Max Size**: 10MB per file
- **Backup Count**: 5 files (50MB total per log type)
- **Encoding**: UTF-8
- **Automatic Cleanup**: Old files automatically removed

## Integration Examples

### FastAPI Route with Logging

```python
from fastapi import APIRouter
from app.utils.logging_utils import get_service_logger

router = APIRouter()
logger = get_service_logger("api")

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    logger.info(f"Fetching user: {user_id}")
    
    try:
        user = await user_service.get_user(user_id)
        logger.info(f"Successfully retrieved user: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Failed to retrieve user {user_id}: {str(e)}")
        raise
```

### Service Class with Logging

```python
from app.utils.logging_utils import ServiceLogger, log_service_method

class UserService:
    def __init__(self):
        self.logger = ServiceLogger("user_service")
    
    @log_service_method("user_service", "create_user")
    async def create_user(self, user_data: dict):
        self.logger.info("Creating new user")
        
        try:
            # User creation logic
            user = await self._create_user_in_db(user_data)
            self.logger.log_operation("user_created", {
                "user_id": user.id,
                "email": user.email
            })
            return user
            
        except Exception as e:
            self.logger.log_error_with_context(e, {
                "operation": "create_user",
                "user_data": {k: v for k, v in user_data.items() if k != "password"}
            })
            raise
```

## Testing

Run the logging test script to verify everything is working:

```bash
python test_logging.py
```

This will:
- Test all logging functions
- Create sample log entries
- Verify log file creation
- Test decorators and utilities

## Monitoring and Alerts

Consider setting up monitoring for:
- **Error Rate**: Monitor error.log for unusual patterns
- **Security Events**: Alert on security.log entries
- **Performance**: Track slow operations in performance logs
- **Disk Usage**: Monitor log file growth

## Best Practices

1. **Use Appropriate Levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General operational information
   - WARNING: Something unexpected happened
   - ERROR: Serious problems that need attention

2. **Include Context**:
   - Always include relevant IDs (user_id, request_id, etc.)
   - Add operation details that help with debugging
   - Use structured data for complex information

3. **Avoid Sensitive Data**:
   - Never log passwords or tokens
   - Sanitize user data before logging
   - Use placeholders for sensitive information

4. **Performance Considerations**:
   - Use appropriate log levels in production
   - Consider async logging for high-traffic applications
   - Monitor log file sizes and rotation

5. **Correlation**:
   - Use request IDs to track requests across services
   - Include user IDs for user-related operations
   - Add operation IDs for complex workflows

## Configuration Files

- `app/config/logging.yaml` - Main logging configuration
- `app/config/logging_config.py` - Logging setup and utilities
- `app/utils/logging_utils.py` - Service logging utilities and decorators
- `test_logging.py` - Comprehensive logging test script

## Dependencies

- `PyYAML` - For YAML configuration parsing
- `logging` - Python standard library (included)
- `pathlib` - Python standard library (included)
