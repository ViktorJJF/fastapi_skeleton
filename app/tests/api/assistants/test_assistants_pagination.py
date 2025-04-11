import pytest
from httpx import AsyncClient

from app.core.config import config


@pytest.mark.asyncio
async def test_get_assistants_paginated(client: AsyncClient):
    """
    Test getting assistants with pagination.
    """
    # First create multiple assistants
    for i in range(5):
        await client.post(
            f"{config.API_V1_STR}/assistants/",
            json={
                "name": f"Paginated Test Assistant {i}",
                "description": f"For testing pagination {i}"
            },
        )
    
    # Get paginated assistants with default parameters
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "items" in data["payload"]
    assert "total" in data["payload"]
    assert "page" in data["payload"]
    assert "size" in data["payload"]
    assert "pages" in data["payload"]
    
    # Default page should be 1
    assert data["payload"]["page"] == 1


@pytest.mark.asyncio
async def test_get_assistants_paginated_custom_params(client: AsyncClient):
    """
    Test getting assistants with custom pagination parameters.
    """
    # Get paginated assistants with custom parameters
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated?page=2&size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    
    # Check the response reflects our custom parameters
    assert data["payload"]["page"] == 2
    assert data["payload"]["size"] == 2
    assert len(data["payload"]["items"]) <= 2  # Should be at most 2 items


@pytest.mark.asyncio
async def test_get_assistants_paginated_invalid_params(client: AsyncClient):
    """
    Test getting assistants with invalid pagination parameters.
    """
    # Test with invalid page number (should default to 1)
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated?page=invalid&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["payload"]["page"] == 1  # Should default to 1
    
    # Test with invalid size (should default to a valid size)
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated?page=1&size=invalid")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert isinstance(data["payload"]["size"], int)  # Should be a valid integer


@pytest.mark.asyncio
async def test_get_assistants_paginated_edge_cases(client: AsyncClient):
    """
    Test edge cases for the paginated assistants endpoint.
    """
    # Test with page beyond available results
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated?page=1000&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert len(data["payload"]["items"]) == 0  # Should return an empty list
    
    # Test with very large size
    response = await client.get(f"{config.API_V1_STR}/assistants/paginated?page=1&size=1000")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    # Should return all items but not crash 