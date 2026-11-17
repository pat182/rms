"""backfill restaurant configurations

Revision ID: 295e5235611b
Revises: 8acd3d9335d4
Create Date: 2026-11-17 08:55:20.824409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '295e5235611b'
down_revision: Union[str, Sequence[str], None] = '8acd3d9335d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create missing restaurant configurations
    op.execute("""
        INSERT INTO restaurant_configurations (
            restaurant_id,
            is_24_hours
        )
        SELECT
            r.id,
            FALSE
        FROM restaurants r
        WHERE NOT EXISTS (
            SELECT 1
            FROM restaurant_configurations rc
            WHERE rc.restaurant_id = r.id
        )
    """)

    # Create missing operating-hour records (Monday = 0, Sunday = 6)
    op.execute("""
        INSERT INTO restaurant_operating_hours (
            configuration_id,
            day_of_week,
            opening_time,
            closing_time,
            is_closed
        )
        SELECT
            rc.id,
            days.day_of_week,
            NULL,
            NULL,
            TRUE
        FROM restaurant_configurations rc
        CROSS JOIN generate_series(0, 6) AS days(day_of_week)
        WHERE NOT EXISTS (
            SELECT 1
            FROM restaurant_operating_hours roh
            WHERE roh.configuration_id = rc.id
              AND roh.day_of_week = days.day_of_week
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
