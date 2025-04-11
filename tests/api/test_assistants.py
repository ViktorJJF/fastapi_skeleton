import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.models.assistant import Assistant


@pytest.mark.asyncio
async def test_create_assistant(client: AsyncClient, test_db: AsyncSession):
    """
    Test creating an assistant.
    """
    response = await client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "name": "Test Assistant",
            "description": "This is a test assistant"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ok"] is True
    assert data["payload"]["name"] == "Test Assistant"
    assert data["payload"]["description"] == "This is a test assistant"
    assert "id" in data["payload"]


@pytest.mark.asyncio
async def test_get_assistants(client: AsyncClient, test_db: AsyncSession):
    """
    Test getting all assistants.
    """
    # First create an assistant
    await client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "name": "List Test Assistant",
            "description": "For testing list endpoint"
        },
    )
    
    # Get all assistants
    response = await client.get(f"{config.API_V1_STR}/assistants/")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert isinstance(data["payload"], list)
    # Check that we have at least one assistant
    assert len(data["payload"]) >= 1


@pytest.mark.asyncio
async def test_get_assistants_paginated(client: AsyncClient, test_db: AsyncSession):
    """
    Test getting assistants with pagination.
    """
    # First create some assistants
    for i in range(3):
        await client.post(
            f"{config.API_V1_STR}/assistants/",
            json={
                "name": f"Paginated Test Assistant {i}",
                "description": f"For testing pagination {i}"
            },
        )
    
    # Get paginated assistants
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert isinstance(data["payload"]["items"], list)
    assert data["payload"]["page"] == 1
    assert data["payload"]["size"] == 2
    assert data["payload"]["total"] >= 3
    assert len(data["payload"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_assistant(client: AsyncClient, test_db: AsyncSession):
    """
    Test getting a specific assistant by ID.
    """
    # First create an assistant
    create_response = await client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "name": "Get Test Assistant",
            "description": "For testing get endpoint"
        },
    )
    assistant_id = create_response.json()["payload"]["id"]
    
    # Get the assistant by ID
    get_response = await client.get(f"{config.API_V1_STR}/assistants/{assistant_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["ok"] is True
    assert data["payload"]["name"] == "Get Test Assistant"
    assert data["payload"]["description"] == "For testing get endpoint"
    assert data["payload"]["id"] == assistant_id


@pytest.mark.asyncio
async def test_update_assistant(client: AsyncClient, test_db: AsyncSession):
    """
    Test updating an assistant.
    """
    # First create an assistant
    create_response = await client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "name": "Update Test Assistant",
            "description": "Original description"
        },
    )
    assistant_id = create_response.json()["payload"]["id"]
    
    # Update the assistant
    update_response = await client.put(
        f"{config.API_V1_STR}/assistants/{assistant_id}",
        json={
            "description": "Updated description"
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["ok"] is True
    assert data["payload"]["name"] == "Update Test Assistant"
    assert data["payload"]["description"] == "Updated description"
    assert data["payload"]["id"] == assistant_id


@pytest.mark.asyncio
async def test_delete_assistant(client: AsyncClient, test_db: AsyncSession):
    """
    Test deleting an assistant.
    """
    # First create an assistant
    create_response = await client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "name": "Delete Test Assistant",
            "description": "For testing delete endpoint"
        },
    )
    assistant_id = create_response.json()["payload"]["id"]
    
    # Delete the assistant
    delete_response = await client.delete(f"{config.API_V1_STR}/assistants/{assistant_id}")
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["ok"] is True
    assert "message" in data
    
    # Verify the assistant is gone
    get_response = await client.get(f"{config.API_V1_STR}/assistants/{assistant_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_assistant(client: AsyncClient, test_db: AsyncSession):
    """
    Test getting a nonexistent assistant.
    """
    response = await client.get(f"{config.API_V1_STR}/assistants/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert "error" in data


@pytest.mark.asyncio
async def test_update_nonexistent_assistant(client: AsyncClient, test_db: AsyncSession):
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
async def test_delete_nonexistent_assistant(client: AsyncClient, test_db: AsyncSession):
    """
    Test deleting a nonexistent assistant.
    """
    response = await client.delete(f"{config.API_V1_STR}/assistants/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert "error" in data 