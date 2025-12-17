"""Initial migration

Revision ID: 20251213_163
Create Date: 2025-12-13T16:33:58.399434
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '20251213_163'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.execute('''CREATE TABLE usefields (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);''')


def downgrade() -> None:
    """Downgrade database schema."""
    op.execute('''DROP TABLE IF EXISTS usefields;''')
