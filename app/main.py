from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger

from app.routes.v1.api import api_router
from app.core.config import config
from app.database.redis import redis_client  # Import from database package instead of direct file
from app.middlewares.logging_middleware import logging_middleware
from app.utils.error_handling import setup_global_exception_handler


def create_application() -> FastAPI:
    """
    Create FastAPI application.
    """
    # Set up global exception handler for uncaught exceptions
    setup_global_exception_handler()
    
    # Create FastAPI app
    app = FastAPI(
        title=config.PROJECT_NAME,
        openapi_url=f"{config.API_V1_STR}/openapi.json",
        debug=config.DEBUG,
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
    app.middleware("http")(logging_middleware)

    # Include API router
    app.include_router(api_router, prefix=config.API_V1_STR)

    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up application")
        try:
            # Connect to Redis
            await redis_client.connect()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application")
        try:
            # Close Redis connection
            await redis_client.close()
            logger.info("Disconnected from Redis")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
