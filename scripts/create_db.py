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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default connection string for PostgreSQL server (not database specific)
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/postgres"


def parse_db_url(url):
    """Parse database URL to extract db_name and connection string to default db."""
    # Extract components from URL using regex
    # Format: postgresql://user:password@host:port/dbname
    pattern = r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)"
    match = re.match(pattern, url)

    if not match:
        return None, url

    user, password, host, port, db_name = match.groups()
    conn_str = f"postgresql://{user}:{password}@{host}:{port}/postgres"

    return db_name, conn_str


def create_database(args):
    """Create the database if it doesn't exist."""
    if args.conn:
        conn_str = args.conn
        db_name = args.name or "albedo"
    else:
        database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
        extracted_db_name, conn_str = parse_db_url(database_url)
        db_name = args.name or extracted_db_name or "albedo"

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
    parser.add_argument(
        "--name",
        "-n",
        help="Database name (default: extracted from DATABASE_URL or 'albedo')",
    )
    parser.add_argument(
        "--conn",
        "-c",
        help="PostgreSQL connection string to default database (default: derived from DATABASE_URL)",
    )

    args = parser.parse_args()
    return create_database(args)


if __name__ == "__main__":
    sys.exit(main())
