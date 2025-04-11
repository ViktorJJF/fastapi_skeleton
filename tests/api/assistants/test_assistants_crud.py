import pytest
from httpx import AsyncClient

from app.core.config import config


@pytest.mark.asyncio
async def test_create_assistant(client: AsyncClient):
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
async def test_get_assistants(client: AsyncClient):
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
async def test_get_assistant(client: AsyncClient):
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
async def test_update_assistant(client: AsyncClient):
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
async def test_delete_assistant(client: AsyncClient):
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