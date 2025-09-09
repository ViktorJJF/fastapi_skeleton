"""
Authentication routes.
"""

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import auth_controller
from app.schemas.auth import (
    LoginRequest,  # Need LoginRequest schema for adapting form data
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.user import UserCreate
from app.database.connection import get_db  # Corrected import path
from app.schemas.core.responses import (
    ApiResponse,
    SingleItemResponse,  # Import standard response types
)

# Potentially add dependencies if needed later
# from app.dependencies.security import get_current_active_user

router = APIRouter()

# --- Auth Routes ---


@router.post(
    "/register", response_model=SingleItemResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Controller needs to return dict compatible with SingleItemResponse or adapt response here
    return await auth_controller.register(user_in=user_in, request=request, db=db)


@router.post("/login", response_model=ApiResponse)  # Response likely contains token
async def login_for_access_token(
    request: Request,
    response: Response,  # Add response parameter
    # Remove form_data dependency
    # form_data: OAuth2PasswordRequestForm = Depends(),
    # Add login_data to accept JSON body based on LoginRequest schema
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user via JSON payload and return access token."""
    # Remove the manual schema creation
    # login_request_schema = LoginRequest(email=form_data.username, password=form_data.password)
    # Pass the received login_data directly to the controller
    return await auth_controller.login(login_data=login_data, request=request, db=db)


@router.post(
    "/verify", response_model=ApiResponse
)  # Response likely just status/message
async def verify_user_email(
    verify_data: VerifyEmailRequest,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Verify user's email address."""
    return await auth_controller.verify_email(
        verify_data=verify_data, request=request, db=db
    )


@router.post(
    "/forgot-password", response_model=ApiResponse
)  # Response likely just status/message
async def request_password_reset(
    forgot_data: ForgotPasswordRequest,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset email."""
    return await auth_controller.forgot_password(
        forgot_data=forgot_data, request=request, db=db
    )


@router.post(
    "/reset-password", response_model=ApiResponse
)  # Response likely just status/message
async def perform_password_reset(
    reset_data: ResetPasswordRequest,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Reset user's password using a token."""
    return await auth_controller.reset_password(
        reset_data=reset_data, request=request, db=db
    )


# Example Token Refresh Endpoint (if implemented)
# @router.get("/token", response_model=ApiResponse) ...
