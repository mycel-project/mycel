"""migrate old slots to 1

Revision ID: d1001fbf0b72
Revises: 64a976086bf0
Create Date: 2026-06-28 15:22:11.919890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1001fbf0b72'
down_revision: Union[str, Sequence[str], None] = '64a976086bf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE learning_units SET slot = 1 WHERE slot = 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE learning_units SET slot = 0 WHERE slot = 1")
