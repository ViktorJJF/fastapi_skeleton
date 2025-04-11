import pytest
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.main import app


@pytest.mark.asyncio
async def test_database_dependency():
    """
    Test that the database dependency is properly configured.
    This verifies our application's dependency injection setup works correctly.
    """
    # Get the dependency
    dependency = get_db
    
    # Check it's a dependency
    assert callable(dependency)
    
    # Ensure it's registered in the app's dependency injection system
    # This is a basic check - we're just making sure the dependency exists
    # and is callable, not that it returns the correct value, which would
    # require actually calling it (done in integration tests)
    assert any(
        d.dependency == get_db 
        for route in app.routes 
        for d in getattr(route, "dependencies", [])
    ) or any(
        d.dependency == get_db
        for route in app.routes
        if hasattr(route, "app")
        for app_route in getattr(route, "routes", [])
        for d in getattr(app_route, "dependencies", [])
    ) 