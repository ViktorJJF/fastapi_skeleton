"""
Cities routes.
"""
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import city_controller
from app.database.connection import get_db
from app.schemas.city import CityCreate, CityUpdate
from app.utils.error_handling import handle_error

router = APIRouter()

@router.get("/", response_model=dict)
async def list_cities(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List all cities.
    """
    try:
        return await city_controller.list_all(request, db)
    except Exception as error:
        return handle_error(response, error)

@router.get("/paginated", response_model=dict)
async def list_cities_paginated(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    List cities with pagination.
    """
    try:
        return await city_controller.list_paginated(request, db)
    except Exception as error:
        return handle_error(response, error)

@router.get("/{id}", response_model=dict)
async def get_city(
    id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a city by ID.
    """
    try:
        return await city_controller.get_one(id, db)
    except Exception as error:
        return handle_error(response, error)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_city(
    city_in: CityCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new city.
    """
    try:
        return await city_controller.create(city_in, db)
    except Exception as error:
        return handle_error(response, error)

@router.put("/{id}", response_model=dict)
async def update_city(
    id: str,
    city_in: CityUpdate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a city.
    """
    try:
        return await city_controller.update(id, city_in, db)
    except Exception as error:
        return handle_error(response, error)

@router.delete("/{id}", response_model=dict)
async def delete_city(
    id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a city.
    """
    try:
        return await city_controller.delete(id, db)
    except Exception as error:
        return handle_error(response, error) 