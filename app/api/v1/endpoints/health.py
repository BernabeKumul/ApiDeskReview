from fastapi import APIRouter
from typing import Dict, Any
from app.services.database import database_service
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def hello_world() -> Dict[str, str]:
    """
    Hello World endpoint - Basic test endpoint.
    """
    return {"message": "Hello World! FastAPI is running successfully! 🚀"}


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify API and MongoDB status.
    """
    # Verificar estado de MongoDB
    mongodb_status = await database_service.health_check()
    
    # Determinar estado general
    overall_status = "healthy" if mongodb_status["status"] == "connected" else "degraded"
    
    return {
        "status": overall_status,
        "message": "API health check completed",
        "version": settings.app_version,
        "services": {
            "api": {
                "status": "healthy",
                "message": "API is running correctly"
            },
            "mongodb": mongodb_status
        }
    }


@router.get("/health/mongodb")
async def mongodb_health_check() -> Dict[str, Any]:
    """
    MongoDB specific health check endpoint.
    """
    return await database_service.health_check()


@router.get("/info")
async def app_info() -> Dict[str, Any]:
    """
    Application information endpoint.
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "description": "FastAPI backend with MongoDB, Qdrant, and OpenAI integration ready",
        "endpoints": {
            "health": "/api/v1/health",
            "hello": "/api/v1/",
            "info": "/api/v1/info",
            "mongodb_health": "/api/v1/health/mongodb",
            "ai_documents": "/api/v1/ai-documents"
        },
        "database": {
            "type": "MongoDB",
            "database_name": settings.mongodb_database
        }
    }