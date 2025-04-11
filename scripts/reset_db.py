#!/usr/bin/env python3
"""
Reset the database by dropping and recreating it.
This script should be used with caution as it DELETES ALL DATA.
"""

import os
import sys
import psycopg2
import logging
import argparse
import re
from scripts.create_db import create_database, parse_db_url

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default connection string for PostgreSQL server (not database specific)
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/postgres"


def drop_database(args):
    """Drop the database if it exists."""
    if args.conn:
        conn_str = args.conn
        db_name = args.name or "albedo"
    else:
        database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        extracted_db_name, conn_str = parse_db_url(database_url)
        db_name = args.name or extracted_db_name or "albedo"
    
    force = args.force

    if not force:
        confirm = input(f"⚠️ WARNING: This will DELETE ALL DATA in the '{db_name}' database. Are you sure? (y/N): ")
        if confirm.lower() != 'y':
            logger.info("Operation cancelled")
            return 0

    logger.info(f"Attempting to drop database: {db_name}")
    
    try:
        # Connect to the default postgres database first
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True  # Needed for DROP DATABASE
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Database '{db_name}' does not exist, nothing to drop")
        else:
            # Terminate all connections to the database
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
            """)
            
            # Drop the database
            cursor.execute(f"DROP DATABASE {db_name}")
            logger.info(f"Database '{db_name}' dropped successfully")
        
        cursor.close()
        conn.close()
        return 0
    except Exception as e:
        logger.error(f"Failed to drop database: {str(e)}")
        return 1


def reset_database(args):
    """Reset the database by dropping and recreating it."""
    # First drop the database
    drop_result = drop_database(args)
    if drop_result != 0:
        return drop_result
    
    # Then create the database again
    create_result = create_database(args)
    if create_result == 0:
        logger.info("Database reset successful")
    
    return create_result


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Database reset utility")
    parser.add_argument("--name", "-n", help="Database name (default: extracted from DATABASE_URL or 'albedo')")
    parser.add_argument("--conn", "-c", help="PostgreSQL connection string to default database (default: derived from DATABASE_URL)")
    parser.add_argument("--force", "-f", action="store_true", help="Force reset without confirmation")
    
    args = parser.parse_args()
    return reset_database(args)


if __name__ == "__main__":
    sys.exit(main()) 