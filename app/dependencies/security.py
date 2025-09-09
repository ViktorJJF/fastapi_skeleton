from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from pydantic import ValidationError
import uuid

from app.database.connection import get_db
from app.core.config import config
from app.utils.security import decode_access_token
from app.schemas.auth import TokenPayload
from app.schemas.user import User, UserInToken
from app.controllers import auth_controller  # To find user by ID

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{config.API_V1_STR}/auth/login",  # Use corrected config object
    scopes={  # Define available roles/scopes
        "USER": "Read information for the current user.",
        "ADMIN": "Read and write all information.",
        "SUPERADMIN": "Manage everything.",
    },
)


async def get_current_user(
    security_scopes: SecurityScopes,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> UserInToken:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception

        # Convert user_id from string back to UUID if needed
        try:
            token_user_id = uuid.UUID(payload.sub)
        except ValueError:
            raise credentials_exception

        # Fetch user from DB to ensure they still exist and are active (optional but recommended)
        # user = await auth_controller._find_user_by_id(token_user_id, db)
        # if user is None:
        #     raise credentials_exception
        # if not user.is_active: # Assuming an is_active field exists
        #     raise HTTPException(status_code=400, detail="Inactive user")

        # Use data directly from token payload if DB check is skipped
        token_data = UserInToken(
            id=token_user_id, role=payload.role, email=payload.email
        )

    except (JWTError, ValidationError) as e:
        print(f"JWT/Validation Error: {e}")  # Log the error
        raise credentials_exception

    # Check permissions based on scopes
    if (
        security_scopes.scopes
    ):  # If specific scopes (roles) are required by the endpoint
        # Get user role from token
        user_role = token_data.role
        if user_role not in security_scopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return token_data


# Dependency to get the current active user (can add checks like is_active)
def get_current_active_user(
    current_user: UserInToken = Security(
        get_current_user, scopes=[]
    )  # No specific scope needed just to be logged in
) -> UserInToken:
    # Add checks here if needed, e.g., if user.is_active
    return current_user


# Dependency for specific roles
def require_role(required_role: str):
    """Dependency factory to require a specific role."""

    def role_checker(
        current_user: UserInToken = Security(get_current_user, scopes=[required_role])
    ) -> UserInToken:
        # The role check is already handled by get_current_user's scope check
        return current_user

    return role_checker


# Dependency factory for multiple roles
def require_roles(required_roles: list[str]):
    """Dependency factory to require one of several roles."""

    def roles_checker(
        current_user: UserInToken = Security(get_current_user, scopes=required_roles)
    ) -> UserInToken:
        # The role check is handled by get_current_user's scope check
        return current_user

    return roles_checker


# Specific role dependencies
require_user = require_role("USER")
require_admin = require_role("ADMIN")
require_superadmin = require_role("SUPERADMIN")
require_admin_or_superadmin = require_roles(["ADMIN", "SUPERADMIN"])
require_any_role = require_roles(["USER", "ADMIN", "SUPERADMIN"])
