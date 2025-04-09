import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import SQLAlchemy models so they are known to Alembic
from app.database.connection import Base
from app.core.config import settings

# Import all models to ensure they're discovered by SQLAlchemy
from app.models import base, user, assistant, entity

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL in the Alembic configuration dynamically
# This ensures we're always using the correct connection string
# For migrations, use synchronous driver
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", db_url)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Set naming convention for constraints following SQLAlchemy best practices
# This helps ensure consistent naming across different databases
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Apply naming convention
Base.metadata.naming_convention = naming_convention


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects for autogenerate detection.
    Return True to include the object in autogeneration, False to exclude it.
    """
    # Exclude specific tables if needed (e.g., third-party tables, spatial tables)
    if type_ == "table" and name in ["spatial_ref_sys"]:
        return False
    
    # You can add more rules here
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        # Compare types to detect column type changes
        compare_type=True,
        # Compare server defaults to detect default value changes
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations in a transaction with proper configuration."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
        # Enable transaction per migration
        transaction_per_migration=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# Modified to use synchronous engine instead of async
def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Create synchronous engine with retry logic
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Try to connect to the database with retries
    retries = 5
    retry_delay = 1  # seconds
    for attempt in range(retries):
        try:
            with connectable.connect() as connection:
                do_run_migrations(connection)
            break
        except Exception as e:
            if attempt < retries - 1:
                print(f"Database connection failed (attempt {attempt+1}/{retries}): {str(e)}")
                import time
                time.sleep(retry_delay)
                # Exponential backoff
                retry_delay *= 2
            else:
                raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 