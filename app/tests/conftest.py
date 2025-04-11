import os
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import get_db
from app.models.base import BaseModel
from app.core.config import config


# This fixture runs once per session
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# This fixture provides a database session for testing
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Use a test database that's separate from the production database
    test_db_url = os.environ.get("TEST_DATABASE_URL", config.DATABASE_URL) 
    if test_db_url.startswith("postgresql://"):
        test_db_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Create an engine with echo for debugging
    engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create and yield a session
    async with async_session() as session:
        yield session
        # Roll back changes after the test is done
        await session.rollback()
    
    # Drop tables when done
    async with engine.begin() as conn:
        try:
            # Disable foreign key checks temporarily to allow dropping tables with dependencies
            await conn.execute(text("SET session_replication_role = 'replica';"))
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.execute(text("SET session_replication_role = 'origin';"))
        except Exception as e:
            print(f"Error dropping tables: {e}")
    
    # Dispose of the engine
    await engine.dispose()


# This fixture provides a test client that uses the test database
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override the get_db dependency to use our test database session
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.rollback()
    
    # Store the original dependency
    original_get_db = app.dependency_overrides.get(get_db)
    
    # Replace with our test dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client using httpx.AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Restore the original dependency
    if original_get_db:
        app.dependency_overrides[get_db] = original_get_db
    else:
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
        
        # Create and yield client - use app=app for HTTPX
        async with AsyncClient(base_url="http://test", app=app) as ac:
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