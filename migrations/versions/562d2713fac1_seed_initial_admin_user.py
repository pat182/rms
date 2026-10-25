"""seed initial admin user

Revision ID: 562d2713fac1
Revises: e1ba1fe56803
Create Date: 2026-10-19 15:10:34.079755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = '562d2713fac1'
down_revision: Union[str, Sequence[str], None] = 'e1ba1fe56803'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    password_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    hashed_password = password_context.hash("test123!@#")

    result = op.get_bind().execute(
        sa.text("""
            INSERT INTO users (
                role_id,
                first_name,
                last_name,
                email,
                password_hash,
                is_active
            )
            VALUES (
                1,
                'patrick',
                'chua',
                'thebackdoors182@gmail.com',
                :password_hash,
                TRUE
            )
            RETURNING id
        """),
        {"password_hash": hashed_password},
    )

    user_id = result.scalar_one()

    op.execute(
        sa.text("""
            INSERT INTO restaurant_users (
                restaurant_id,
                user_id
            )
            VALUES (
                1,
                :user_id
            )
        """).bindparams(user_id=user_id)
    )




def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM restaurant_users
            WHERE user_id IN (
                SELECT id FROM users
                WHERE email = 'thebackdoors182@gmail.com'
            )
        """)
    )

    op.execute(
        sa.text("""
            DELETE FROM users
            WHERE email = 'thebackdoors182@gmail.com'
        """)
    )
