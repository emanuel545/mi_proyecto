"""create user order order item tables

Revision ID: 4cc7ea261131
Revises:
Create Date: 2026-04-27 11:35:32.250546

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "4cc7ea261131"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
