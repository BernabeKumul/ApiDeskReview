from fastapi import APIRouter
from app.api.v1.endpoints import health, ai_documents, audit, vector_search

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

api_router.include_router(
    audit.router,
    prefix="",
    tags=["Audit"]
)

api_router.include_router(
    vector_search.router,
    prefix="",
    tags=["Vector Search"]
)