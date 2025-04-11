import pytest
from httpx import AsyncClient

from app.core.config import config


@pytest.mark.asyncio
async def test_app_loads_without_errors(client: AsyncClient):
    """
    Test that the application loads without errors by checking the health endpoint.
    This verifies that our FastAPI app can be initialized properly.
    """
    response = await client.get(f"{config.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 