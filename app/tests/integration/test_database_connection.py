import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(test_db: AsyncSession):
    """
    Test that the database connection works by executing a simple query.
    This ensures our database setup is correct.
    """
    # Simple query to check if connection works
    result = await test_db.execute(text("SELECT 1"))
    value = result.scalar()
    
    # Verify we got a result
    assert value == 1 