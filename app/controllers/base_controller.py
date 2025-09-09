from typing import Any, Dict, List, Optional, Type, Generic, TypeVar
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.connection import Base, get_db
from app.utils.db_helpers import (
    get_all_items,
    get_items,
    get_item,
    create_item,
    update_item,
    delete_item,
    check_query_string,
)
from app.utils.error_handling import (
    build_error_object,
    item_not_found,
    item_already_exists,
    handle_error,
    is_id_valid,
)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)


class BaseController(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, GetSchemaType]
):
    """
    Base controller with CRUD operations.
    """

    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        get_schema: Type[GetSchemaType],
        prefix: str,
        tags: List[str],
        unique_fields: List[str] = [],
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.get_schema = get_schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.unique_fields = unique_fields
        self.setup_routes()

    async def item_exists_excluding_itself(
        self, db: AsyncSession, id: int, data: Dict[str, Any]
    ) -> bool:
        """
        Check if an item exists with the same unique fields, excluding itself.
        """
        if not self.unique_fields:
            return False

        query = db.query(self.model)

        # Add conditions for unique fields
        for field in self.unique_fields:
            if field in data:
                query = query.filter(getattr(self.model, field) == data[field])

        # Exclude the current item
        query = query.filter(self.model.id != id)

        # Check if any item exists
        result = await db.execute(query)
        item = result.scalars().first()

        return item is not None

    async def item_exists(self, db: AsyncSession, data: Dict[str, Any]) -> bool:
        """
        Check if an item exists with the same unique fields.
        """
        if not self.unique_fields:
            return False

        query = db.query(self.model)

        # Add conditions for unique fields
        for field in self.unique_fields:
            if field in data:
                query = query.filter(getattr(self.model, field) == data[field])

        # Check if any item exists
        result = await db.execute(query)
        item = result.scalars().first()

        return item is not None

    def handle_error(self, response: Response, error: Any) -> Response:
        """
        Handle error and return appropriate response.
        """
        return handle_error(error)

    def setup_routes(self):
        """
        Setup routes for CRUD operations.
        """

        @self.router.get("/", response_model=Dict[str, Any])
        async def list_all(request: Request, db: AsyncSession = Depends(get_db)):
            """
            Get all items.
            """
            try:
                items = await get_all_items(db, self.model)
                return {
                    "ok": True,
                    "payload": [
                        self.get_schema.model_validate(item).model_dump(mode="json")
                        for item in items
                    ],
                }
            except Exception as e:
                raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

        @self.router.get("/paginated", response_model=Dict[str, Any])
        async def list_paginated(request: Request, db: AsyncSession = Depends(get_db)):
            """
            Get paginated items with filtering.
            """
            try:
                query_params = dict(request.query_params)
                processed_query = await check_query_string(query_params)
                result = await get_items(db, self.model, request, processed_query)

                # Convert items to schema
                result.items = [
                    self.get_schema.model_validate(item).model_dump(mode="json")
                    for item in result.items
                ]

                return {
                    "ok": True,
                    "payload": result.items,
                    "pagination": {
                        "total": result.total,
                        "page": result.page,
                        "size": result.size,
                        "pages": result.pages,
                    },
                }
            except Exception as e:
                raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

        @self.router.get("/{id}", response_model=Dict[str, Any])
        async def get_one(id: str, db: AsyncSession = Depends(get_db)):
            """
            Get a single item by ID.
            """
            try:
                valid_id = is_id_valid(id)
                item = await get_item(db, self.model, valid_id)
                return {
                    "ok": True,
                    "payload": self.get_schema.model_validate(item).model_dump(
                        mode="json"
                    ),
                }
            except HTTPException as e:
                raise e
            except Exception as e:
                raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

        @self.router.post(
            "/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED
        )
        async def create(
            item_in: self.create_schema, db: AsyncSession = Depends(get_db)
        ):
            """
            Create a new item.
            """
            try:
                # Check if item with unique fields already exists
                if await self.item_exists(db, item_in.dict()):
                    raise build_error_object(
                        status.HTTP_409_CONFLICT,
                        "Item with these unique fields already exists",
                    )

                # Create item
                item = await create_item(db, self.model, item_in.dict())
                return {
                    "ok": True,
                    "payload": self.get_schema.model_validate(item).model_dump(
                        mode="json"
                    ),
                }
            except HTTPException as e:
                raise e
            except Exception as e:
                raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

        @self.router.put("/{id}", response_model=Dict[str, Any])
        async def update(
            id: str, item_in: self.update_schema, db: AsyncSession = Depends(get_db)
        ):
            """
            Update an existing item.
            """
            try:
                valid_id = is_id_valid(id)

                # Check if item with unique fields already exists (excluding this item)
                if await self.item_exists_excluding_itself(
                    db, valid_id, item_in.dict(exclude_unset=True)
                ):
                    raise build_error_object(
                        status.HTTP_409_CONFLICT,
                        "Item with these unique fields already exists",
                    )

                # Update item
                item = await update_item(
                    db, self.model, valid_id, item_in.dict(exclude_unset=True)
                )
                return {
                    "ok": True,
                    "payload": self.get_schema.model_validate(item).model_dump(
                        mode="json"
                    ),
                }
            except HTTPException as e:
                raise e
            except Exception as e:
                raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

        @self.router.delete("/{id}", response_model=Dict[str, Any])
        async def delete(id: str, db: AsyncSession = Depends(get_db)):
            """
            Delete an item.
            """
            try:
                valid_id = is_id_valid(id)
                item = await delete_item(db, self.model, valid_id)
                return {
                    "ok": True,
                    "payload": self.get_schema.model_validate(item).model_dump(
                        mode="json"
                    ),
                }
            except HTTPException as e:
                raise e
            except Exception as e:
                raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
