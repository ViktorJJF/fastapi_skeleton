"""
Assistants routes.
"""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import assistant_controller
from app.database.connection import get_db
from app.schemas.assistant import (
    AssistantCreate,
    AssistantUpdate,
    AssistantDeleteManyInput,
    AssistantResponse,
    AssistantPaginatedResponse,
)
from app.schemas.core.paginations import PaginationParams
from app.schemas.core.responses import (
    DeleteResponse,
    DeleteManyResponse,
)
from app.dependencies.security import (
    require_admin_or_superadmin,
    require_superadmin,
)

router = APIRouter()


@router.get(
    "/",
    response_model=AssistantPaginatedResponse,
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def list_assistants(
    request: Request,
    response: Response,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    List assistants with pagination. Requires ADMIN or SUPERADMIN role.
    """
    return await assistant_controller.list_paginated(request, pagination, db)


@router.get(
    "/{id}",
    response_model=AssistantResponse,
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def get_assistant(
    request: Request, response: Response, id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get an assistant by ID. Requires ADMIN or SUPERADMIN role.
    """
    return await assistant_controller.get_one(id, request, db)


@router.post(
    "/",
    response_model=AssistantResponse,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_admin_or_superadmin)],
)
async def create_assistant(
    request: Request,
    response: Response,
    assistant: AssistantCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new assistant. Requires ADMIN or SUPERADMIN role.
    """
    return await assistant_controller.create(assistant, request, db)


@router.put(
    "/{id}",
    response_model=AssistantResponse,
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def update_assistant(
    request: Request,
    response: Response,
    id: int,
    assistant: AssistantUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an assistant. Requires ADMIN or SUPERADMIN role.
    """
    return await assistant_controller.update(id, assistant, request, db)


@router.delete(
    "/{id}",
    response_model=DeleteResponse,
    dependencies=[Depends(require_admin_or_superadmin)],
)
async def delete_assistant(
    request: Request, response: Response, id: int, db: AsyncSession = Depends(get_db)
):
    """
    Delete an assistant. Requires ADMIN or SUPERADMIN role.
    """
    return await assistant_controller.delete(id, request, db)


@router.delete(
    "/batch",
    response_model=DeleteManyResponse,
    dependencies=[Depends(require_superadmin)],
)
async def delete_assistants(
    request: Request,
    response: Response,
    item: AssistantDeleteManyInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete multiple assistants. Requires SUPERADMIN role.

    Body Parameters:
    - ids: List of assistant IDs to delete
    """
    return await assistant_controller.delete_many(request, item, db)
