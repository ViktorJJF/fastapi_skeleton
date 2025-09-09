import os
import redis.asyncio as aioredis
import uvicorn
from contextlib import asynccontextmanager
from typing import Tuple
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.routes.v1.api import api_router
from app.core.config import config
from app.core import logger as _  # Import to ensure logger setup is loaded
from app.database.redis import (
    redis_client,
)  # Import from database package instead of direct file
from app.database.connection import engine

# from app.middlewares.logging_middleware import logging_middleware
from app.utils.error_handling import setup_global_exception_handler, handle_error


# --- Database connection test function ---
async def test_database_connection() -> Tuple[bool, str]:
    """Test database connectivity and return status with error details."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()  # fetchone() is not async, don't await it
            return True, ""
    except SQLAlchemyError as e:
        error_msg = str(e)
        logger.error(f"Database connection failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error testing database connection: {error_msg}")
        return False, error_msg


# --- Service status logging functions ---
def log_startup_banner():
    """Log application startup banner with key information."""
    logger.info(f"🚀 Starting {config.PROJECT_NAME}")
    logger.info(f"📊 Environment: {'Development' if config.DEBUG else 'Production'}")


def log_service_endpoints():
    """Log available service endpoints."""
    base_url = f"http://localhost:{config.PORT}"

    logger.info(f"  📚 API Documentation: {base_url}/docs")


def log_service_status(db_connected: bool, redis_connected: bool, db_error: str = ""):
    """Log final service status summary."""
    # Database status
    if db_connected:
        logger.info("🗄️  Database: ✅ Connected")
    else:
        logger.error("🗄️  Database: ❌ Failed")
        if db_error:
            logger.error(f"   Error: {db_error}")

    # Redis status
    if redis_connected:
        logger.info("🔴 Redis: ✅ Connected")
    else:
        logger.error("🔴 Redis: ❌ Failed")

    logger.info(f"🌟 {config.PROJECT_NAME} running on http://localhost:{config.PORT}")


# --- Define the exception handler ---
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Custom handler for FastAPI validation errors."""
    logger.warning(f"Caught validation error: {exc.errors()}")
    # Use our existing handle_error function
    return await handle_error(request, exc)


def create_application() -> FastAPI:
    """
    Create FastAPI application.
    """
    # Set up global exception handler for uncaught exceptions
    setup_global_exception_handler()

    # Define lifespan context manager
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup logic
        log_startup_banner()

        # Initialize service connection status
        db_connected = False
        db_error = ""
        redis_connected = False

        logger.info("🔌 Connecting to services...")

        # Test database connection
        try:
            db_connected, db_error = await test_database_connection()
        except Exception as e:
            db_connected = False
            db_error = str(e)

        # Test Redis connection with retries
        redis_connected = False
        max_retries = 3
        retry_delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                await redis_client.connect()
                redis_connected = True
                break
            except Exception as e:
                if attempt < max_retries:
                    import asyncio

                    await asyncio.sleep(retry_delay)
                else:
                    redis_connected = False
        logger.info(f"Application running in port: {config.PORT}")
        # Log available endpoints
        log_service_endpoints()

        # Log final service status
        log_service_status(db_connected, redis_connected, db_error)

        # Yield control to FastAPI
        yield

        # Shutdown logic
        logger.info("🛑 Shutting down application...")
        try:
            # Close Redis connection
            if redis_connected:
                await redis_client.close()
                logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.warning(f"⚠️  Error closing Redis connection: {e}")

        logger.info("👋 Application shutdown complete")

    # Create FastAPI app with lifespan context manager
    app = FastAPI(
        title=config.PROJECT_NAME,
        openapi_url=f"{config.API_V1_STR}/openapi.json",
        debug=config.DEBUG,
        lifespan=lifespan,
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    # app.middleware("http")(logging_middleware)

    # Include API router
    app.include_router(api_router, prefix=config.API_V1_STR)

    # --- Register the custom handler AFTER app creation ---
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    return app


app = create_application()


if __name__ == "__main__":
    logger.info(f"🌟 Starting {config.PROJECT_NAME} on port {config.PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT)
