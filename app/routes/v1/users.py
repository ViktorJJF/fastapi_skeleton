from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import user_controller
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    User as UserSchema,
    UserDeleteManyInput,
)
from app.schemas.core.paginations import PaginationParams
from app.db.session import get_db  # Corrected import path
from app.dependencies.security import (
    get_current_active_user,
    require_admin_or_superadmin,
    require_superadmin,
)
from app.schemas.user import UserInToken
from app.schemas.core.responses import (
    SingleItemResponse,
    PaginatedApiResponse,
    DeleteResponse,
    DeleteManyResponse,
    ListResponse,
)

router = APIRouter()

# --- User CRUD Routes ---


@router.post(
    "/",
    response_model=SingleItemResponse,  # Use standard response model
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def create_user(
    user_in: UserCreate,
    request: Request,
    response: Response,  # Add response parameter like assistants.py
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    # Controller already returns JSONResponse, adapt if needed or expect controller to return dict
    return await user_controller.create(item=user_in, request=request, db=db)


@router.put(
    "/{user_id}",
    response_model=SingleItemResponse,  # Use standard response model
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Update a user by ID."""
    # Consider adding user permission check (update self vs update others)
    return await user_controller.update(
        id=user_id, item=user_in, request=request, db=db
    )


@router.delete(
    "/{user_id}",
    response_model=DeleteResponse,  # Use standard response model
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def delete_user(
    user_id: str,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Delete a user by ID."""
    return await user_controller.delete(id=user_id, request=request, db=db)


@router.post(
    "/delete-many",  # Changed path to match assistant batch delete
    response_model=DeleteManyResponse,  # Use standard response model
    dependencies=[Depends(require_superadmin)],
)
async def delete_multiple_users(
    delete_input: UserDeleteManyInput,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple users by their IDs."""
    return await user_controller.delete_many(request=request, item=delete_input, db=db)


@router.get(
    "/{user_id}",
    response_model=SingleItemResponse,  # Use standard response model
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def read_user(
    user_id: str,
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user by ID."""
    return await user_controller.get_one(id=user_id, request=request, db=db)


@router.get(
    "/all",
    response_model=ListResponse,  # Use standard response model
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def read_users_all(
    request: Request,
    response: Response,  # Add response parameter
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all users."""
    return await user_controller.list_all(request=request, db=db)


@router.get(
    "/",
    response_model=PaginatedApiResponse,  # Use standard response model
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def read_users_paginated(
    request: Request,
    response: Response,  # Add response parameter
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve users with pagination."""
    return await user_controller.list_paginated(
        request=request, pagination=pagination, db=db
    )


# Endpoint for users to get their own info
@router.get("/me", response_model=SingleItemResponse)  # Use standard response model
async def read_user_me(
    request: Request,
    response: Response,  # Add response parameter
    current_user: UserInToken = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's information."""
    # Use the get_one controller function but pass the current user's ID
    return await user_controller.get_one(
        id=str(current_user.id), request=request, db=db
    )
