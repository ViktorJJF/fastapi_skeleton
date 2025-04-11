import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import get_db
from app.models.base import BaseModel
from app.core.config import config

# Define fixture for consistent event loop usage
@pytest_asyncio.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test function."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Session-scoped engine fixture
@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Creates a test database engine once per session."""
    test_db_url = os.environ.get("TEST_DATABASE_URL", config.DATABASE_URL) 
    if test_db_url.startswith("postgresql://"):
        test_db_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(test_db_url, echo=False, future=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    yield engine
    
    # Drop tables
    async with engine.begin() as conn:
        try:
            await conn.execute(text("SET session_replication_role = 'replica';"))
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.execute(text("SET session_replication_role = 'origin';"))
        except Exception as e:
            print(f"Error dropping tables: {e}")
    
    await engine.dispose()


# Function-scoped session fixture with explicit transaction control
@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine, event_loop: asyncio.AbstractEventLoop) -> AsyncGenerator[AsyncSession, None]:
    """Creates a new database session with explicit transaction control."""
    # Connect and begin a transaction explicitly
    connection = await test_engine.connect()
    
    # Start a transaction explicitly
    transaction = await connection.begin()
    
    # Create a session bound to this connection
    session = AsyncSession(bind=connection, expire_on_commit=False)
    
    try:
        # Yield the session for test use
        yield session
    finally:
        # Always close the session
        await session.close()
        
        # Roll back the transaction, discarding all changes
        if transaction.is_active:
            await transaction.rollback()
            
        # Return the connection to the pool
        await connection.close()


# Corrected client fixture using AsyncClient with app
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient that uses the test database session."""

    # Override the get_db dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            # Rollback is handled by the db_session fixture
            pass

    original_get_db = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    # Use a proper test client
    test_client = TestClient(app)
    
    # Create a wrapper to allow using test_client in async code
    async def get_response(method, url, **kwargs):
        response = getattr(test_client, method)(url, **kwargs)
        return response
    
    # Use AsyncClient for compatibility with the rest of the tests
    ac = AsyncClient()
    
    # Monkey patch the methods we need
    ac.get = lambda url, **kwargs: get_response("get", url, **kwargs)
    ac.post = lambda url, **kwargs: get_response("post", url, **kwargs)
    ac.put = lambda url, **kwargs: get_response("put", url, **kwargs)
    ac.delete = lambda url, **kwargs: get_response("delete", url, **kwargs)
    
    yield ac

    # Restore original dependency
    if original_get_db:
        app.dependency_overrides[get_db] = original_get_db
    else:
        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]


# This fixture provides a FastAPI app with a test database session dependency
@pytest_asyncio.fixture
async def test_app(db_session: AsyncSession) -> FastAPI:
    # Override the get_db dependency to use our test database
    async def override_get_db():
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise
    
    # Override the dependency in the app
    app.dependency_overrides[get_db] = override_get_db
    
    yield app
    
    # Clean up
    app.dependency_overrides.clear()


# Alternative client fixture using the same pattern as FastAPI docs
@pytest_asyncio.fixture
async def fastapi_client() -> AsyncClient:
    """
    Alternative client fixture that follows FastAPI documentation pattern.
    
    This is more similar to the FastAPI testing docs example, where the
    application setup and client creation are done directly in the fixture.
    """
    # Set up test database dependency
    test_db_url = os.environ.get("TEST_DATABASE_URL", config.DATABASE_URL)
    if test_db_url.startswith("postgresql://"):
        test_db_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    # Create engine and session for this test only
    engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with TestingSessionLocal() as session:
        # Override dependency
        async def override_get_db():
            try:
                yield session
            finally:
                await session.rollback()
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Use a proper test client
        test_client = TestClient(app)
        
        # Create a wrapper to allow using test_client in async code
        async def get_response(method, url, **kwargs):
            response = getattr(test_client, method)(url, **kwargs)
            return response
        
        # Use AsyncClient for compatibility with the rest of the tests
        ac = AsyncClient()
        
        # Monkey patch the methods we need
        ac.get = lambda url, **kwargs: get_response("get", url, **kwargs)
        ac.post = lambda url, **kwargs: get_response("post", url, **kwargs)
        ac.put = lambda url, **kwargs: get_response("put", url, **kwargs)
        ac.delete = lambda url, **kwargs: get_response("delete", url, **kwargs)
        
        yield ac
        
        # Clean up
        app.dependency_overrides.clear()
    
    # Clean up database - use CASCADE to handle dependencies
    async with engine.begin() as conn:
        # Set foreign_key_constraint_on_delete to CASCADE
        await conn.execute(text("SET session_replication_role = 'replica';"))
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.execute(text("SET session_replication_role = 'origin';"))
    
    await engine.dispose() 