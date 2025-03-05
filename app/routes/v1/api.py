"""
API router for v1 endpoints.
"""
from fastapi import APIRouter

from app.routes.v1 import cities, entities, assistants

# Create API router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

# Include route modules
api_router.include_router(
    cities.router, prefix="/cities", tags=["cities"]
)
api_router.include_router(
    assistants.router, prefix="/assistants", tags=["assistants"]
)
api_router.include_router(
    entities.router, prefix="", tags=["entities"]
) 