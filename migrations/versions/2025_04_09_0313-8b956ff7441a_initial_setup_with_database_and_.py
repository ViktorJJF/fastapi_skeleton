"""initial setup with database and assistant table

Revision ID: 8b956ff7441a
Revises: 
Create Date: 2025-04-09 03:13:59.087127

"""
from alembic import op
import sqlalchemy as sa
import logging

# revision identifiers, used by Alembic.
revision = '8b956ff7441a'
down_revision = None
branch_labels = None
depends_on = None

# Setup logging
logger = logging.getLogger('alembic.migration')


def upgrade() -> None:
    """
    Upgrade operations.
    
    This function creates the initial database schema with the assistants
    table and related entities.
    """
    # Create the assistants table
    logger.info("Creating assistants table")
    op.create_table(
        'assistants',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_assistants'))
    )
    
    # Create the entities table for assistant relationships
    logger.info("Creating entities table")
    op.create_table(
        'entities',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('assistant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['assistant_id'], ['assistants.id'], name=op.f('fk_entities_assistant_id_assistants')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_entities'))
    )
    
    # Create indexes
    logger.info("Creating indexes")
    op.create_index(op.f('ix_assistants_id'), 'assistants', ['id'], unique=False)
    op.create_index(op.f('ix_entities_id'), 'entities', ['id'], unique=False)
    op.create_index(op.f('ix_entities_assistant_id'), 'entities', ['assistant_id'], unique=False)
    
    # Create updated_at trigger for assistants table
    logger.info("Creating timestamp triggers")
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        op.execute("""
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
           NEW.updated_at = now(); 
           RETURN NEW;
        END;
        $$ language 'plpgsql';
        """)
        
        op.execute("""
        CREATE TRIGGER update_assistants_timestamp
        BEFORE UPDATE ON assistants
        FOR EACH ROW EXECUTE FUNCTION update_timestamp();
        """)
        
        op.execute("""
        CREATE TRIGGER update_entities_timestamp
        BEFORE UPDATE ON entities
        FOR EACH ROW EXECUTE FUNCTION update_timestamp();
        """)


def downgrade() -> None:
    """
    Downgrade operations.
    
    This function should revert all changes made in the upgrade function.
    Operations should be performed in REVERSE order.
    """
    logger.info("Removing indexes and tables")
    
    # First drop the entities table (has foreign key to assistants)
    op.drop_index(op.f('ix_entities_assistant_id'), table_name='entities')
    op.drop_index(op.f('ix_entities_id'), table_name='entities')
    op.drop_table('entities')
    
    # Then drop the assistants table
    op.drop_index(op.f('ix_assistants_id'), table_name='assistants')
    op.drop_table('assistants')
    
    # Drop the triggers and functions if PostgreSQL
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        logger.info("Removing triggers and functions")
        op.execute("DROP TRIGGER IF EXISTS update_assistants_timestamp ON assistants")
        op.execute("DROP TRIGGER IF EXISTS update_entities_timestamp ON entities")
        op.execute("DROP FUNCTION IF EXISTS update_timestamp()")


# Additional functions for complex migration logic
# def _migrate_data():
#     """Helper function for complex data migrations"""
#     pass 