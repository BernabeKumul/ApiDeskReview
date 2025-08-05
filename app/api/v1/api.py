from fastapi import APIRouter
from app.api.v1.endpoints import health, ai_documents

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="",
    tags=["Health & Hello World"]
)

api_router.include_router(
    ai_documents.router,
    prefix="",
    tags=["AI Documents"]
)