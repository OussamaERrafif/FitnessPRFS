# FitnessPR Backend API

A comprehensive FastAPI-based backend for fitness personal record tracking and trainer-client management.

## Features Implemented

### Core Features
- ✅ User Authentication (JWT-based)
- ✅ User Registration & Login
- ✅ Role-based Access Control (Client, Trainer, Admin)
- ✅ SQLite Database with SQLAlchemy ORM
- ✅ Comprehensive Data Models
- ✅ API Documentation with Swagger/OpenAPI
- ✅ **Global Logging System** - Comprehensive logging to `/logs` folder

### Infrastructure Features
- ✅ **Centralized Logging**: YAML-configured logging system
- ✅ **Multiple Log Files**: Separate logs for app, API, security, errors, and debug
- ✅ **Request Tracking**: Automatic HTTP request logging with unique IDs
- ✅ **Performance Monitoring**: Built-in performance metrics logging
- ✅ **Security Logging**: Dedicated security event tracking
- ✅ **Log Rotation**: Automatic log file rotation and cleanup

### Database Models
- ✅ **Users**: Authentication and basic profile
- ✅ **Clients**: Client-specific fitness profiles
- ✅ **Trainers**: Trainer profiles and professional info
- ✅ **Exercises**: Exercise library with categories and details
- ✅ **Progress Logs**: Workout tracking and personal records
- ✅ **Programs**: Training program management
- ✅ **Session Bookings**: Trainer-client appointment scheduling
- ✅ **Meal Plans**: Nutrition planning and tracking

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (already set up)

### Installation & Setup

1. **Activate Virtual Environment** (if not already active):
   ```powershell
   .\Scripts\activate
   ```

2. **Install Dependencies** (already installed):
   ```powershell
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   The `.env` file is already configured for development.

4. **Start the Development Server**:
   ```powershell
   python start_dev.py
   ```

5. **Access the API**:
   - API Base URL: `http://127.0.0.1:8000`
   - Interactive Docs: `http://127.0.0.1:8000/docs`
   - Alternative Docs: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile
- `POST /api/v1/auth/change-password` - Change password

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user by ID

### Health
- `GET /health` - Health check endpoint
- `GET /api/v1/health` - API health check

## Example Usage

### 1. Register a New User
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "password": "password123",
    "full_name": "John Doe",
    "role": "client"
  }'
```

### 2. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 3. Access Protected Endpoints
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Schema

### Key Relationships
- **User** → **Client** (1:1)
- **User** → **Trainer** (1:1)
- **Client** → **Trainer** (Many:1 - assigned trainer)
- **User** → **ProgressLog** (1:Many)
- **Exercise** → **ProgressLog** (1:Many)
- **Client** → **Program** (1:Many)
- **Trainer** → **Program** (1:Many)
- **Client** → **SessionBooking** (1:Many)
- **Trainer** → **SessionBooking** (1:Many)
- **Client** → **MealPlan** (1:Many)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── session.py           # Database session config
│   ├── api/
│   │   ├── deps.py          # Dependencies and auth
│   │   └── routes.py        # API routes
│   ├── config/
│   │   └── config.py        # Settings and configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── trainer.py
│   │   ├── exercise.py
│   │   ├── progress_log.py
│   │   ├── program.py
│   │   ├── session_booking.py
│   │   └── meal_plan.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   └── user.py
│   └── services/            # Business logic
│       └── auth_service.py
├── .env                     # Environment variables
├── pyproject.toml          # Project configuration
├── start_dev.py            # Development server script
├── test_api.py             # API test script
└── fitness_pr.db           # SQLite database (auto-created)
```

## Configuration

Key settings in `.env`:
- `DATABASE_URL`: SQLite database path
- `SECRET_KEY`: JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (30 minutes)
- `DEBUG`: Enable debug mode (True for development)

## Logging System

The application includes a comprehensive logging system that logs everything to the `/logs` folder:

### Log Files
- `app.log` - General application logs
- `error.log` - Error logs only
- `debug.log` - Debug information (when debug mode enabled)
- `api.log` - API requests and responses (JSON format)
- `security.log` - Security events and authentication

### Features
- **Automatic Request Logging**: Every HTTP request is logged with unique IDs
- **Performance Monitoring**: Request timing and performance metrics
- **Security Tracking**: Authentication attempts and security events
- **Error Context**: Detailed error information with stack traces
- **Log Rotation**: Automatic file rotation at 10MB with 5 backup files

### Usage
```python
from app.config.logging_config import get_logger
from app.utils.logging_utils import get_service_logger

# Basic logging
logger = get_logger(__name__)
logger.info("Something happened")

# Service logging with decorators
service_logger = get_service_logger("my_service")
service_logger.log_operation("user_created", {"user_id": "123"})
```

**📖 For detailed logging documentation, see [LOGGING.md](LOGGING.md)**

### Testing the Logging System
```bash
python test_logging.py
```

## Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Role-based access control
- ✅ CORS configuration
- ✅ Request validation with Pydantic
- ✅ SQL injection prevention with SQLAlchemy

## Development Tools

- **Testing**: Run `python test_api.py` for basic endpoint testing
- **Docs**: Interactive API documentation at `/docs`
- **Database**: SQLite browser or any SQLite client
- **Logs**: Console logging with configurable levels

## Next Steps for Development

### High Priority
1. **Exercise Management**: CRUD operations for exercises
2. **Progress Logging**: Record and retrieve workout data
3. **Trainer-Client Relationships**: Assignment and management
4. **Session Booking**: Schedule and manage training sessions

### Medium Priority
1. **Program Management**: Create and assign training programs
2. **Meal Planning**: Nutrition tracking and meal plans
3. **File Uploads**: Handle exercise images/videos
4. **Notifications**: Email/SMS notifications for sessions

### Future Enhancements
1. **Real-time Features**: WebSocket support for live updates
2. **Analytics**: Progress tracking and reporting
3. **Mobile API**: Optimized endpoints for mobile apps
4. **Integration**: Third-party fitness trackers and services

## Database Migration

The application automatically creates database tables on startup. For production, consider using Alembic migrations:

```powershell
# Initialize migrations (future)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **Server won't start**: Check if port 8000 is available
2. **Database errors**: Ensure write permissions in the directory
3. **Token errors**: Check SECRET_KEY configuration
4. **Import errors**: Verify virtual environment is activated

### Logs
The application logs startup information and database operations. Check the console output for detailed information.

## Contributing

1. Follow the existing code structure
2. Add appropriate type hints
3. Include docstrings for new functions
4. Test new endpoints with the test script
5. Update this README for new features

## License

MIT License - see LICENSE file for details.
