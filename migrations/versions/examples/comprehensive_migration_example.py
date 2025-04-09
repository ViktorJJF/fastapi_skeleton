"""Comprehensive migration example with best practices

Revision ID: example_revision
Revises: previous_revision
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table, column
import logging

# Import any models if needed for data migrations
# from app.models.example import ExampleModel

# revision identifiers, used by Alembic.
revision = 'example_revision'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

# Setup logging
logger = logging.getLogger('alembic.migration')


def upgrade() -> None:
    """
    Upgrade operations with examples of various migration patterns.
    
    This example demonstrates:
    1. Table creation with constraints and indexes
    2. Data migration strategies
    3. Constraint naming conventions
    4. Adding triggers and functions
    5. Batch migration techniques for SQLite
    6. Safe column removal
    """
    # Part 1: Schema changes - create a new table
    # ============================================
    logger.info("Creating users table")
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('email', name=op.f('uq_users_email')),
        sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    
    # Create indexes - using consistent naming
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Part 2: Add columns to existing table
    # =====================================
    # Adding a column to an existing table
    logger.info("Adding columns to products table")
    op.add_column('products', sa.Column('is_featured', sa.Boolean(), server_default='false', nullable=False))
    
    # Part 3: Batch operations for SQLite compatibility
    # ================================================
    # Use batch operations for SQLite which has limitations on ALTER TABLE
    # This will automatically create temp tables for SQLite and use ALTER TABLE for others
    logger.info("Performing batch operations on orders table")
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tracking_number', sa.String(length=100), nullable=True))
        batch_op.create_index(batch_op.f('ix_orders_tracking_number'), ['tracking_number'], unique=False)
    
    # Part 4: Data migration
    # =====================
    # Example of data migration with raw SQL for performance
    logger.info("Migrating data")
    op.execute("""
    UPDATE products SET is_featured = true 
    WHERE id IN (SELECT id FROM products ORDER BY sales_count DESC LIMIT 10)
    """)
    
    # Alternative: data migration using SQLAlchemy Core for portability
    # Define a table representation for use with SQLAlchemy Core
    products = table('products',
        column('id', sa.Integer),
        column('is_featured', sa.Boolean),
        column('created_at', sa.DateTime)
    )
    
    # Execute an update
    op.execute(
        products.update().where(
            products.c.created_at > sa.text("'2023-01-01'")
        ).values(
            is_featured=True
        )
    )
    
    # Part 5: Adding database functions and triggers
    # ============================================
    logger.info("Adding database functions and triggers")
    
    # PostgreSQL-specific function and trigger for updating 'updated_at'
    # Check for PostgreSQL dialect
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        # Create a function to update timestamp
        op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)
        
        # Create a trigger that uses this function
        op.execute("""
        CREATE TRIGGER set_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """)
    
    # Part 6: Safe enum handling
    # =========================
    # Create a new enum type
    logger.info("Adding ENUM type")
    user_role_enum = postgresql.ENUM('admin', 'user', 'guest', name='user_role_enum')
    if conn.dialect.name == 'postgresql':
        user_role_enum.create(op.get_bind(), checkfirst=True)
        
        # Add column using the enum
        op.add_column('users', sa.Column(
            'role', 
            postgresql.ENUM('admin', 'user', 'guest', name='user_role_enum'), 
            server_default='user',
            nullable=False
        ))
    else:
        # For other databases, use a string with check constraint
        op.add_column('users', sa.Column(
            'role', 
            sa.String(50), 
            server_default='user',
            nullable=False
        ))
        op.create_check_constraint(
            'ck_users_role_valid',
            'users',
            "role IN ('admin', 'user', 'guest')"
        )


def downgrade() -> None:
    """
    Downgrade operations - must reverse all changes in reverse order.
    
    WARNING: Testing downgrade operations is critical before using in production.
    """
    # Get connection to check dialect
    conn = op.get_bind()
    
    # Part 6: Remove enum type
    logger.info("Removing role column and enum type")
    op.drop_column('users', 'role')
    if conn.dialect.name == 'postgresql':
        # Drop the enum type
        postgresql.ENUM(name='user_role_enum').drop(op.get_bind(), checkfirst=True)
    
    # Part 5: Remove triggers and functions
    logger.info("Removing database functions and triggers")
    if conn.dialect.name == 'postgresql':
        op.execute("DROP TRIGGER IF EXISTS set_updated_at ON users;")
        op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Part 4: No need to revert data migrations, as schema changes will reset it
    
    # Part 3: Revert batch operations
    logger.info("Reverting batch operations on orders table")
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_orders_tracking_number'))
        batch_op.drop_column('tracking_number')
    
    # Part 2: Remove added columns
    logger.info("Removing columns from products table")
    op.drop_column('products', 'is_featured')
    
    # Part 1: Drop created tables (including all constraints and indexes)
    logger.info("Dropping users table")
    op.drop_table('users')


# Helper functions for complex operations
def _update_user_data():
    """Example of a helper function for complex data migrations."""
    pass


# Usage example:
# def upgrade():
#     # ... schema changes ...
#     _update_user_data()
#     # ... more schema changes ... 