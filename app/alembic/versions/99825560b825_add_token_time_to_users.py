"""add token_time to users

Revision ID: 99825560b825
Revises: 75857bb567e3
Create Date: 2026-08-26 10:45:50.321313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99825560b825'
down_revision: Union[str, Sequence[str], None] = '75857bb567e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
