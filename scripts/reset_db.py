#!/usr/bin/env python3
"""
Reset database script - drops existing tables and resets migration state.
This is used to reset the database to apply table name changes.
"""

import os
import sys
import psycopg2
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connection string for the database
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/albedo_db")
if DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql://", 1)


def reset_database():
    """Drop all tables and reset alembic version."""
    logger.info("Resetting database...")
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(DB_URL)
        connection = engine.connect()
        
        # Start a transaction
        trans = connection.begin()
        
        try:
            # Drop tables with CASCADE to handle dependencies
            logger.info("Dropping tables...")
            connection.execute(text("DROP TABLE IF EXISTS entity CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS assistant CASCADE"))
            
            # Remove migration version
            logger.info("Resetting migration state...")
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
            
            # Commit the transaction
            trans.commit()
            logger.info("Database reset successfully")
            
        except Exception as e:
            # Roll back on error
            trans.rollback()
            logger.error(f"Error during reset: {str(e)}")
            raise
        finally:
            connection.close()
            
        return 0
    except Exception as e:
        logger.error(f"Failed to reset database: {str(e)}")
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    sys.exit(reset_database()) 