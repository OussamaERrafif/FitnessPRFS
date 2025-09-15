from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from app.config.config import settings
from app.config.logging_config import setup_logging, get_logger, log_request_info, log_performance
from app.session import create_tables
from app.api.routes import api_router

# Setup global logging configuration
setup_logging()

# Get logger for this module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up FitnessPR API...")
    create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FitnessPR API...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        description="A comprehensive fitness tracking and personal record management API",
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests and responses with detailed information."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Get client information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log incoming request
        api_logger = get_logger("app.api.requests")
        api_logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": request.headers.get("content-type", ""),
                "content_length": request.headers.get("content-length", ""),
                "timestamp": time.time()
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            api_logger.info(
                f"Response: {response.status_code} for {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(process_time * 1000, 2),
                    "timestamp": time.time()
                }
            )
            
            # Log performance metrics
            log_performance(
                operation=f"{request.method} {request.url.path}",
                duration=process_time,
                details={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            
            # Log slow requests
            if process_time > 1.0:  # Log requests taking more than 1 second
                slow_logger = get_logger("app.api.slow")
                slow_logger.warning(
                    f"Slow Request: {request.method} {request.url.path} took {process_time:.3f}s",
                    extra={
                        "request_id": request_id,
                        "duration": process_time,
                        "endpoint": f"{request.method} {request.url.path}",
                        "client_ip": client_ip
                    }
                )
            
        except Exception as e:
            # Log request errors
            process_time = time.time() - start_time
            error_logger = get_logger("app.api.errors")
            error_logger.error(
                f"Request Error: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration": process_time,
                    "endpoint": f"{request.method} {request.url.path}",
                    "client_ip": client_ip
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for production
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["your-domain.com", "www.your-domain.com"]
        )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return JSONResponse(
            content={
                "status": "healthy",
                "version": settings.version,
                "environment": settings.environment
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return JSONResponse(
            content={
                "message": "Welcome to FitnessPR API",
                "version": settings.version,
                "docs": "/docs" if settings.debug else "Documentation disabled in production"
            }
        )
    
    return app


# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
