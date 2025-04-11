import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database.connection import get_db
from app.core.config import config


@pytest.mark.asyncio
async def test_create_city():
    """
    Test creating a city.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"{config.API_V1_STR}/cities/",
            json={
                "name": "New York",
                "country": "USA",
                "description": "The Big Apple"
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ok"] is True
        assert data["payload"]["name"] == "New York"
        assert data["payload"]["country"] == "USA"
        assert data["payload"]["description"] == "The Big Apple"
        assert "id" in data["payload"]


@pytest.mark.asyncio
async def test_get_cities():
    """
    Test getting all cities.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"{config.API_V1_STR}/cities/")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert isinstance(data["payload"], list)


@pytest.mark.asyncio
async def test_get_city():
    """
    Test getting a city by ID.
    """
    # First create a city
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            f"{config.API_V1_STR}/cities/",
            json={
                "name": "Los Angeles",
                "country": "USA",
                "description": "City of Angels"
            },
        )
        city_id = create_response.json()["payload"]["id"]
        
        # Now get the city
        get_response = await client.get(f"{config.API_V1_STR}/cities/{city_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["ok"] is True
        assert data["payload"]["name"] == "Los Angeles"
        assert data["payload"]["country"] == "USA"
        assert data["payload"]["description"] == "City of Angels"


@pytest.mark.asyncio
async def test_update_city():
    """
    Test updating a city.
    """
    # First create a city
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            f"{config.API_V1_STR}/cities/",
            json={
                "name": "Chicago",
                "country": "USA",
                "description": "The Windy City"
            },
        )
        city_id = create_response.json()["payload"]["id"]
        
        # Now update the city
        update_response = await client.put(
            f"{config.API_V1_STR}/cities/{city_id}",
            json={
                "description": "Updated description"
            },
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["ok"] is True
        assert data["payload"]["name"] == "Chicago"
        assert data["payload"]["country"] == "USA"
        assert data["payload"]["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_city():
    """
    Test deleting a city.
    """
    # First create a city
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            f"{config.API_V1_STR}/cities/",
            json={
                "name": "Miami",
                "country": "USA",
                "description": "Magic City"
            },
        )
        city_id = create_response.json()["payload"]["id"]
        
        # Now delete the city
        delete_response = await client.delete(f"{config.API_V1_STR}/cities/{city_id}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["ok"] is True
        
        # Try to get the deleted city
        get_response = await client.get(f"{config.API_V1_STR}/cities/{city_id}")
        assert get_response.status_code == 404 