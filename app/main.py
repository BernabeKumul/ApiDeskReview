from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.services.database import database_service


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        description="FastAPI backend with MongoDB, Qdrant, and OpenAI integration ready",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    
    # Include API routers
    app.include_router(
        api_router,
        prefix="/api/v1"
    )
    
    return app


# Create the FastAPI application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.
    """
    print(f"🚀 {settings.app_name} v{settings.app_version} is starting up...")
    print(f"📍 Running on {settings.host}:{settings.port}")
    print(f"📚 Documentation available at: http://{settings.host}:{settings.port}/docs")
    
    # Conectar a MongoDB
    try:
        await database_service.connect()
        print("✅ MongoDB connection established successfully")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("⚠️  Application will continue but database operations will fail")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    """
    print(f"🛑 {settings.app_name} is shutting down...")
    
    # Desconectar de MongoDB
    try:
        await database_service.disconnect()
        print("✅ MongoDB disconnected successfully")
    except Exception as e:
        print(f"❌ Error disconnecting from MongoDB: {e}")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with basic API information.
    """
    return {
        "message": f"Welcome to {settings.app_name}!",
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }