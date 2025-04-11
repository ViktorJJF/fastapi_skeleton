import pytest
from httpx import AsyncClient

from app.core.config import config


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """
    Test that the health endpoint returns the expected response.
    """
    response = await client.get(f"{config.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 