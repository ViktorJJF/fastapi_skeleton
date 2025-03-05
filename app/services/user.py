from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.repositories.user import user_repository
from app.core.security import create_access_token
from app.db.redis import redis_client


class UserService:
    """
    Service for user operations.
    """
    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[UserSchema]:
        """
        Get a user by ID.
        """
        user = await user_repository.get(db, user_id)
        if user:
            return UserSchema.from_orm(user)
        return None

    async def get_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[UserSchema]:
        """
        Get multiple users with pagination.
        """
        users = await user_repository.get_multi(db, skip=skip, limit=limit)
        return [UserSchema.from_orm(user) for user in users]

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> UserSchema:
        """
        Create a new user.
        """
        # Check if user with same email or username already exists
        user_by_email = await user_repository.get_by_email(db, email=user_in.email)
        if user_by_email:
            raise ValueError("Email already registered")
        
        user_by_username = await user_repository.get_by_username(db, username=user_in.username)
        if user_by_username:
            raise ValueError("Username already taken")
        
        # Create user
        user = await user_repository.create(db, obj_in=user_in)
        logger.info(f"User created: {user.username}")
        return UserSchema.from_orm(user)

    async def update_user(
        self, db: AsyncSession, user_id: int, user_in: UserUpdate
    ) -> Optional[UserSchema]:
        """
        Update a user.
        """
        user = await user_repository.get(db, user_id)
        if not user:
            return None
        
        # Update user
        user = await user_repository.update(db, db_obj=user, obj_in=user_in)
        logger.info(f"User updated: {user.username}")
        return UserSchema.from_orm(user)

    async def delete_user(self, db: AsyncSession, user_id: int) -> Optional[UserSchema]:
        """
        Delete a user.
        """
        user = await user_repository.get(db, user_id)
        if not user:
            return None
        
        # Delete user
        user = await user_repository.remove(db, id=user_id)
        logger.info(f"User deleted: {user.username}")
        return UserSchema.from_orm(user)

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[dict]:
        """
        Authenticate a user and return access token.
        """
        user = await user_repository.authenticate(db, username=username, password=password)
        if not user:
            return None
        
        # Check if user is active
        if not await user_repository.is_active(user):
            return None
        
        # Create access token
        access_token = create_access_token(subject=user.id)
        
        # Cache user data in Redis
        user_data = UserSchema.from_orm(user).dict()
        await redis_client.set(
            f"user:{user.id}",
            str(user_data),
            expire=60 * 60  # 1 hour
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(user)
        }


# Create a singleton instance
user_service = UserService() 