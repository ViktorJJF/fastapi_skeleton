"""
Assistants routes.
"""
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.controllers import assistant_controller
from app.database.connection import get_db
from app.schemas.assistant import AssistantCreate, AssistantUpdate, AssistantDeleteManyInput, Assistant
from app.schemas.core.paginations import PaginationParams
from app.schemas.core.responses import (
    ApiResponse, SingleItemResponse, ListResponse, 
    PaginatedApiResponse, DeleteResponse, DeleteManyResponse
)

router = APIRouter()

@router.get("/all", response_model=ListResponse)
async def list_all_assistants(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List all assistants.
    """
    return await assistant_controller.list_all(request, db)

@router.get("/", response_model=PaginatedApiResponse)
async def list_assistants(
    request: Request,
    response: Response,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    List assistants with pagination.
    """
    return await assistant_controller.list_paginated(request, pagination, db)

@router.get("/{id}", response_model=SingleItemResponse)
async def get_assistant(
    request: Request,
    response: Response,
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an assistant by ID.
    """
    return await assistant_controller.get_one(id, request, db)

@router.post("/", response_model=SingleItemResponse, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    request: Request,
    response: Response,
    assistant: AssistantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new assistant.
    """
    return await assistant_controller.create(assistant, request, db)

@router.put("/{id}", response_model=SingleItemResponse)
async def update_assistant(
    request: Request,
    response: Response,
    id: int,
    assistant: AssistantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an assistant.
    """
    return await assistant_controller.update(id, assistant, request, db)

@router.delete("/{id}", response_model=DeleteResponse)
async def delete_assistant(
    request: Request,
    response: Response,
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an assistant.
    """
    return await assistant_controller.delete(id, request, db)

# batch delete
@router.delete("/batch", response_model=DeleteManyResponse)
async def delete_assistants(
    request: Request,
    response: Response,
    item: AssistantDeleteManyInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete multiple assistants.
    
    Body Parameters:
    - ids: List of assistant IDs to delete
    """
    return await assistant_controller.delete_many(request, item, db)
