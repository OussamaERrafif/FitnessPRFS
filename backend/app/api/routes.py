from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "0.1.0"
    }

# Import v1 API routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.clients import router as clients_router
from app.api.v1.trainers import router as trainers_router
from app.api.v1.exercises import router as exercises_router
from app.api.v1.progress import router as progress_router
from app.api.v1.programs import router as programs_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.meals import router as meals_router
from app.api.v1.notifications import router as notifications_router

# Include v1 API routers
api_router.include_router(auth_router, prefix="/v1")
api_router.include_router(users_router, prefix="/v1")
api_router.include_router(clients_router, prefix="/v1")
api_router.include_router(trainers_router, prefix="/v1")
api_router.include_router(exercises_router, prefix="/v1")
api_router.include_router(progress_router, prefix="/v1")
api_router.include_router(programs_router, prefix="/v1")
api_router.include_router(sessions_router, prefix="/v1")
api_router.include_router(meals_router, prefix="/v1")
api_router.include_router(notifications_router, prefix="/v1")
