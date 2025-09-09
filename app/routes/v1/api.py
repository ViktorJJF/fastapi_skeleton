"""
API router for v1 endpoints.
"""

from fastapi import APIRouter

# Correct imports from app/routes/v1
from app.routes.v1 import (
    assistants,
    users,
    auth,
)

# Create API router
api_router = APIRouter()


# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Include user routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Include other existing routers using the correct variables
api_router.include_router(assistants.router, prefix="/assistants", tags=["Assistants"])
