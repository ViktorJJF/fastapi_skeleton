from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.schemas.token import Token
from app.services.user import user_service
from app.db.session import get_db


class AuthController:
    """
    Controller for authentication operations.
    """
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        """
        Setup routes for authentication operations.
        """
        @self.router.post("/login", response_model=Token)
        async def login(
            form_data: OAuth2PasswordRequestForm = Depends(),
            db: AsyncSession = Depends(get_db)
        ):
            """
            OAuth2 compatible token login, get an access token for future requests.
            """
            result = await user_service.authenticate_user(
                db, form_data.username, form_data.password
            )
            if not result:
                logger.warning(f"Failed login attempt for user: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.info(f"User logged in: {form_data.username}")
            return {
                "access_token": result["access_token"],
                "token_type": result["token_type"],
                "user": result["user"]
            }


# Create a singleton instance
auth_controller = AuthController() 