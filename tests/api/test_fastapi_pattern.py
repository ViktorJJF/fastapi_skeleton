import pytest
from httpx import AsyncClient

from app.core.config import config


@pytest.mark.asyncio
async def test_health_fastapi_pattern(fastapi_client: AsyncClient):
    """
    Test the health endpoint using the alternative fastapi_client fixture.
    
    This demonstrates how to use the fixture that follows FastAPI documentation pattern.
    """
    response = await fastapi_client.get(f"{config.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_assistants_fastapi_pattern(fastapi_client: AsyncClient):
    """
    Test creating and retrieving an assistant using the alternative fastapi_client fixture.
    
    This demonstrates a more complex test case with the FastAPI documentation pattern.
    """
    # Create an assistant
    create_response = await fastapi_client.post(
        f"{config.API_V1_STR}/assistants/",
        json={
            "name": "FastAPI Pattern Test Assistant",
            "description": "Testing the FastAPI pattern fixture"
        },
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["ok"] is True
    assistant_id = data["payload"]["id"]
    
    # Retrieve the assistant
    get_response = await fastapi_client.get(f"{config.API_V1_STR}/assistants/{assistant_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["ok"] is True
    assert get_data["payload"]["name"] == "FastAPI Pattern Test Assistant"
    assert get_data["payload"]["description"] == "Testing the FastAPI pattern fixture" 