"""add unique active dining session per table

Revision ID: a48ddb2eee8a
Revises: 165c2ade2ab9
Create Date: 2026-11-14 10:44:23.550000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a48ddb2eee8a'
down_revision: Union[str, Sequence[str], None] = '165c2ade2ab9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.create_index(
        "uq_active_dining_session_per_table",
        "dining_sessions",
        ["restaurant_table_id"],
        unique=True,
        postgresql_where=sa.text(
            "is_active IS TRUE AND status IN ('verified', 'pending')"
        ),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_active_dining_session_per_table",
        table_name="dining_sessions",
    )

