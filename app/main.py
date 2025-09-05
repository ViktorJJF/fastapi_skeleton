import os
import redis.asyncio as aioredis
import uvicorn
import logging
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# only for local development
if os.getenv("PYTHON_ENV") == "development":
    from dotenv import load_dotenv
    load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.routes.v1.api import api_router
from app.core.config import config
from app.database.redis import redis_client  # Import from database package instead of direct file
from app.database.connection import engine
# from app.middlewares.logging_middleware import logging_middleware
from app.utils.error_handling import setup_global_exception_handler, handle_error

logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format for log messages
)

# --- Database connection test function ---
async def test_database_connection() -> bool:
    """Test database connectivity."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()  # fetchone() is not async, don't await it
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing database connection: {e}")
        return False

# --- Service status logging functions ---
def log_startup_banner():
    """Log application startup banner with key information."""
    logger.info("=" * 80)
    logger.info(f"🚀 Starting {config.PROJECT_NAME}")
    logger.info("=" * 80)
    logger.info(f"📊 Environment: {'Development' if config.DEBUG else 'Production'}")
    logger.info(f"🔧 Debug Mode: {config.DEBUG}")
    logger.info(f"🌐 API Version: {config.API_V1_STR}")

def log_service_endpoints():
    """Log available service endpoints."""
    base_url = "http://localhost:4000"  # This could be made configurable
    
    logger.info("-" * 50)
    logger.info("📋 Available Endpoints:")
    logger.info(f"  🏥 Health Check: {base_url}{config.API_V1_STR}/health")
    logger.info(f"  🔐 Authentication: {base_url}{config.API_V1_STR}/auth/*")
    logger.info(f"  👥 Users: {base_url}{config.API_V1_STR}/users/*")
    logger.info(f"  🤖 Assistants: {base_url}{config.API_V1_STR}/assistants/*")
    logger.info(f"  📚 API Documentation: {base_url}/docs")
    logger.info(f"  📋 ReDoc Documentation: {base_url}/redoc")
    logger.info(f"  📄 OpenAPI Schema: {base_url}{config.API_V1_STR}/openapi.json")
    logger.info("-" * 50)

def log_service_status(db_connected: bool, redis_connected: bool):
    """Log final service status summary."""
    logger.info("🔍 Service Status Summary:")
    
    # Database status
    db_status = "✅ Connected" if db_connected else "❌ Failed"
    logger.info(f"  🗄️  Database: {db_status}")
    if not db_connected:
        logger.error("  ⚠️  Database connection failed - some features may not work")
    
    # Redis status  
    redis_status = "✅ Connected" if redis_connected else "❌ Failed"
    logger.info(f"  🔴 Redis: {redis_status}")
    if not redis_connected:
        logger.warning("  ⚠️  Redis connection failed - caching/sessions may not work")
    
    # Overall status
    if db_connected and redis_connected:
        logger.info("🎉 All services connected successfully!")
    elif db_connected or redis_connected:
        logger.warning("⚠️  Some services failed to connect - application may have limited functionality")
    else:
        logger.error("❌ Critical services failed to connect - application may not function properly")
    
    logger.info("=" * 80)
    logger.info(f"🌟 {config.PROJECT_NAME} is now running on http://localhost:4000")
    logger.info("=" * 80)

# --- Define the exception handler --- 
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
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
        redis_connected = False
        
        logger.info("🔌 Initializing service connections...")
        
        # Test database connection
        logger.info("📊 Testing database connection...")
        try:
            db_connected = await test_database_connection()
            if db_connected:
                logger.info("✅ Database connection successful")
            else:
                logger.error("❌ Database connection failed")
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
        
        # Test Redis connection with retries
        logger.info("🔴 Testing Redis connection...")
        redis_connected = False
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                await redis_client.connect()
                redis_connected = True
                logger.info("✅ Redis connection successful")
                break
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"⚠️  Redis connection attempt {attempt} failed: {e}")
                    logger.info(f"🔄 Retrying Redis connection in {retry_delay} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"❌ Redis connection failed after {max_retries} attempts: {e}")
                    redis_connected = False
        
        # Log available endpoints
        log_service_endpoints()
        
        # Log final service status
        log_service_status(db_connected, redis_connected)
            
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
    uvicorn.run("main:app", host="0.0.0.0", port=4000)
