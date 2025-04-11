import logging
import asyncio

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.database.connection import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(db_engine: Engine) -> None:
    """
    Initialize the database connection.
    
    This function attempts to create a database session and execute a simple query
    to verify that the database is available and responsive.
    
    Args:
        db_engine: SQLAlchemy engine to use for connection
        
    Raises:
        Exception: If the database cannot be reached
    """
    session = AsyncSession(db_engine)
    try:
        # Try to create session to check if DB is awake
        await session.execute(text("SELECT 1"))
        await session.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise e
    finally:
        await session.close()


def main() -> None:
    """
    Main entry point for the backend pre-start script.
    
    This function initializes the service by verifying that the database
    connection is working properly.
    """
    logger.info("Initializing service")
    asyncio.run(init(engine))
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main() 