#!/usr/bin/env python3
"""
Create the albedo_db database.
This script should be run before running migrations.
"""

import os
import sys
import argparse
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default connection string for PostgreSQL server (not database specific)
DEFAULT_POSTGRES_URL = "postgresql://postgres:postgres@postgres:5432/postgres"


def create_database(args):
    """Create the database if it doesn't exist."""
    db_name = args.name
    conn_str = args.conn or os.getenv("POSTGRES_URL", DEFAULT_POSTGRES_URL)
    
    # Check if a valid database name was provided
    if not db_name:
        logger.error("Database name is required")
        sys.exit(1)
    
    logger.info(f"Attempting to create database: {db_name}")
    
    try:
        # Connect to the default postgres database first
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True  # Needed for CREATE DATABASE
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if exists:
            logger.info(f"Database '{db_name}' already exists, skipping creation")
        else:
            # Create the database
            cursor.execute(f"CREATE DATABASE {db_name} WITH ENCODING 'UTF8'")
            logger.info(f"Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
        return 0
    except Exception as e:
        logger.error(f"Failed to create database: {str(e)}")
        return 1


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Database creation utility")
    parser.add_argument("--name", "-n", default="albedo_db", help="Database name (default: albedo_db)")
    parser.add_argument("--conn", "-c", help="PostgreSQL connection string (default: environment variable or preset)")
    
    args = parser.parse_args()
    return create_database(args)


if __name__ == "__main__":
    sys.exit(main()) 