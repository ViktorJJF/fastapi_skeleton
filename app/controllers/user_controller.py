from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
import uuid

from app.models.Users import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    User as UserSchema,
    UserDeleteManyInput,
)
from app.schemas.core.paginations import PaginationParams
from app.utils.db_helpers import (
    get_items,
    get_item,
    delete_item,
    check_query_string,
    delete_items_by_ids,
)
from app.utils.error_handling import handle_error, is_id_valid, build_error_object
from app.utils.security import get_password_hash


async def create(item: UserCreate, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Create a new user.
    """
    try:
        # Check if user already exists
        existing_user = await db.execute(select(User).filter(User.email == item.email))
        if existing_user.scalars().first():
            raise build_error_object(
                status.HTTP_400_BAD_REQUEST, "Email already registered"
            )

        # Hash password
        hashed_password = get_password_hash(item.password)

        # Create user instance (without password in the dict)
        user_data = item.model_dump(exclude={"password"})
        db_user = User(**user_data, hashed_password=hashed_password)

        # Add verification token (optional, can be moved to auth controller)
        # db_user.verification_token = uuid.uuid4().hex

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "ok": True,
                "payload": UserSchema.model_validate(db_user).model_dump(),
            },
        )
    except Exception as e:
        await db.rollback()
        return await handle_error(request, e)


async def update(
    id: str, item: UserUpdate, request: Request, db: AsyncSession
) -> JSONResponse:
    """
    Update a user.
    """
    try:
        valid_id = is_id_valid(id)
        db_user = await get_item(db, User, valid_id)
        if not db_user:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "User not found")

        update_data = item.model_dump(exclude_unset=True)

        # Handle password update
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            db_user.hashed_password = hashed_password
            del update_data["password"]  # Remove plain password from update dict

        # Update other fields
        for key, value in update_data.items():
            setattr(db_user, key, value)

        await db.commit()
        await db.refresh(db_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "payload": UserSchema.model_validate(db_user).model_dump(),
            },
        )
    except Exception as e:
        await db.rollback()
        return await handle_error(request, e)


async def delete(id: str, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Delete a user.
    """
    try:
        valid_id = is_id_valid(id)
        deleted = await delete_item(db, User, valid_id)
        if not deleted:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "User not found")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": {"id": str(valid_id), "deleted": True}},
        )
    except Exception as e:
        # No rollback needed for delete usually, but handle_error might
        return await handle_error(request, e)


async def delete_many(
    request: Request, item: UserDeleteManyInput, db: AsyncSession
) -> JSONResponse:
    """
    Delete multiple users by their IDs.
    """
    try:
        valid_ids = []
        invalid_ids = []
        for user_id_str in item.ids:
            try:
                valid_id = is_id_valid(user_id_str)  # Assuming is_id_valid returns UUID
                valid_ids.append(valid_id)
            except HTTPException:
                invalid_ids.append(user_id_str)

        if invalid_ids:
            raise build_error_object(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid User IDs provided: {', '.join(invalid_ids)}",
            )

        if not valid_ids:
            raise build_error_object(
                status.HTTP_400_BAD_REQUEST, "No valid User IDs provided for deletion."
            )

        deleted_count = await delete_items_by_ids(db, User, valid_ids)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "payload": {
                    "deleted_count": deleted_count,
                    "requested_ids": item.ids,
                    "valid_ids_processed": [str(uid) for uid in valid_ids],
                    "invalid_ids_found": invalid_ids,
                },
            },
        )
    except Exception as e:
        await db.rollback()  # Rollback if delete_items_by_ids fails partially
        return await handle_error(request, e)


async def get_one(id: str, request: Request, db: AsyncSession) -> JSONResponse:
    """
    Get one user by ID.
    """
    try:
        valid_id = is_id_valid(id)
        item = await get_item(db, User, valid_id)
        if not item:
            raise build_error_object(status.HTTP_404_NOT_FOUND, "User not found")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "payload": UserSchema.model_validate(item).model_dump(),
            },
        )
    except Exception as e:
        return await handle_error(request, e)

async def list_paginated(
    request: Request, pagination: PaginationParams, db: AsyncSession
) -> JSONResponse:
    """
    List users with pagination.
    """
    try:
        # Specify searchable fields for users
        searchable_fields = "name,email,role"
        # Pass the pagination model directly, add searchable fields if needed
        processed_query = await check_query_string(pagination, User)
        # Add searchable fields if search term exists
        if pagination.search:
            processed_query["fields"] = searchable_fields

        result = await get_items(db, User, request, processed_query)

        # Validate items using User schema
        result_items = [
            UserSchema.model_validate(item).model_dump() for item in result.items
        ]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "payload": {
                    "items": result_items,
                    "total": result.total,
                    "page": result.page,
                    "page_size": result.size,
                    "pages": result.pages,
                },
            },
        )
    except Exception as e:
        return await handle_error(request, e)
