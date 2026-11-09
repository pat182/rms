"""change dining session foreign key delete behavior

Revision ID: 403d9230476e
Revises: 510fc0b6d731
Create Date: 2026-11-09 16:39:05.816329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '403d9230476e'
down_revision: Union[str, Sequence[str], None] = '510fc0b6d731'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "dining_sessions_restaurant_table_id_fkey",
        "dining_sessions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "dining_sessions_restaurant_table_id_fkey",
        "dining_sessions",
        "restaurant_tables",
        ["restaurant_table_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "dining_sessions_restaurant_table_id_fkey",
        "dining_sessions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "dining_sessions_restaurant_table_id_fkey",
        "dining_sessions",
        "restaurant_tables",
        ["restaurant_table_id"],
        ["id"],
        ondelete="CASCADE",
    )
