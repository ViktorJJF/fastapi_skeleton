import pytest
from httpx import AsyncClient

from app.core.config import config


@pytest.mark.asyncio
async def test_get_nonexistent_assistant(client: AsyncClient):
    """
    Test getting a nonexistent assistant.
    """
    response = await client.get(f"{config.API_V1_STR}/assistants/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert "error" in data


@pytest.mark.asyncio
async def test_update_nonexistent_assistant(client: AsyncClient):
    """
    Test updating a nonexistent assistant.
    """
    response = await client.put(
        f"{config.API_V1_STR}/assistants/9999",
        json={
            "name": "Nonexistent Assistant",
            "description": "This assistant doesn't exist"
        },
    )
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert "error" in data


@pytest.mark.asyncio
async def test_delete_nonexistent_assistant(client: AsyncClient):
    """
    Test deleting a nonexistent assistant.
    """
    response = await client.delete(f"{config.API_V1_STR}/assistants/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert "error" in data


@pytest.mark.asyncio
async def test_create_assistant_validation_error(client: AsyncClient):
    """
    Test creating an assistant with invalid data (missing required field).
    """
    response = await client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "description": "Missing required name field"
        },
    )
    assert response.status_code in [400, 422]  # FastAPI validation errors return 422
    data = response.json()
    assert "detail" in data  # FastAPI returns validation errors as "detail"


@pytest.mark.asyncio
async def test_update_assistant_with_invalid_id(client: AsyncClient):
    """
    Test updating an assistant with an invalid ID format.
    """
    response = await client.put(
        f"{config.API_V1_STR}/assistants/invalid-id",
        json={
            "description": "Updated description"
        },
    )
    assert response.status_code in [400, 404, 422]
    data = response.json()
    assert data["ok"] is False or "detail" in data 