"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """
    Upgrade operations.
    
    This function should handle schema changes for moving from the previous
    revision to this revision.
    
    Guidelines:
    - Group related operations together with comments
    - Use transaction-safe operations where possible
    - Consider validation and error handling
    - Add comments for complex operations
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Downgrade operations.
    
    This function should revert all changes made in the upgrade function.
    Operations should be performed in REVERSE order.
    
    WARNING: Downgrading in production can lead to data loss!
    
    Guidelines:
    - Test downgrade operations thoroughly before using in production
    - For destructive operations (e.g., dropping columns), consider 
      adding safeguards
    """
    ${downgrades if downgrades else "pass"}


# Additional functions for complex migration logic
# def _migrate_data():
#     """Helper function for complex data migrations"""
#     pass 