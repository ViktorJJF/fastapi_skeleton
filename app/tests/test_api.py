import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import get_db
from app.core.config import settings


@pytest.mark.asyncio
async def test_health_check():
    """
    Test health check endpoint.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_user():
    """
    Test creating a user.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"{settings.API_V1_STR}/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data
        assert "password" not in data 