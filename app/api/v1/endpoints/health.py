from fastapi import APIRouter
from typing import Dict, Any

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
    Health check endpoint to verify API status.
    """
    return {
        "status": "healthy",
        "message": "API is running correctly",
        "version": "1.0.0"
    }


@router.get("/info")
async def app_info() -> Dict[str, Any]:
    """
    Application information endpoint.
    """
    return {
        "app_name": "FastAPI Backend",
        "version": "1.0.0",
        "description": "FastAPI backend with MongoDB, Qdrant, and OpenAI integration ready",
        "endpoints": {
            "health": "/api/v1/health",
            "hello": "/api/v1/",
            "info": "/api/v1/info"
        }
    }