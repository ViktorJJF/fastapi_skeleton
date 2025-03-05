"""
Authentication routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth import auth_controller
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()

@router.post("/login", response_model=dict)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint.
    """
    return await auth_controller.login(login_data, db)

@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: TokenResponse,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh token endpoint.
    """
    return await auth_controller.refresh_token(token_data, db) 