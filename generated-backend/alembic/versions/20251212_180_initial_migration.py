"""Initial migration

Revision ID: 20251212_180
Create Date: 2025-12-12T18:07:50.608674
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "20251212_180"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.execute(
        """CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);"""
    )
    op.execute(
        """CREATE TABLE usefields (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);"""
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.execute("""DROP TABLE IF EXISTS todos;""")
    op.execute("""DROP TABLE IF EXISTS usefields;""")
