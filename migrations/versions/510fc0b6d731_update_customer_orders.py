
"""update customer orders

Revision ID: 510fc0b6d731
Revises: 280294bcebfd
Create Date: 2026-11-06 15:10:43.690976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "510fc0b6d731"
down_revision: Union[str, Sequence[str], None] = "280294bcebfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update menu_item foreign key
    op.drop_constraint(
        op.f("customer_order_items_menu_item_id_fkey"),
        "customer_order_items",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "fk_customer_order_items_menu_item_id",
        "customer_order_items",
        "menu_items",
        ["menu_item_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Add restaurant_id and subtotal columns
    op.add_column(
        "customer_orders",
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
    )

    op.add_column(
        "customer_orders",
        sa.Column("subtotal", sa.Numeric(precision=10, scale=2), nullable=False),
    )

    # Create restaurant index
    op.create_index(
        op.f("ix_customer_orders_restaurant_id"),
        "customer_orders",
        ["restaurant_id"],
        unique=False,
    )

    # Update dining_session foreign key
    op.drop_constraint(
        op.f("customer_orders_dining_session_token_fkey"),
        "customer_orders",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "fk_customer_orders_dining_session_token",
        "customer_orders",
        "dining_sessions",
        ["dining_session_token"],
        ["session_token"],
        ondelete="RESTRICT",
    )

    # Create restaurant foreign key
    op.create_foreign_key(
        "fk_customer_orders_restaurant_id",
        "customer_orders",
        "restaurants",
        ["restaurant_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Remove old subtotal column
    op.drop_column("customer_orders", "sub_total")


def downgrade() -> None:
    # Restore old subtotal column
    op.add_column(
        "customer_orders",
        sa.Column(
            "sub_total",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
    )

    # Remove new foreign keys
    op.drop_constraint(
        "fk_customer_orders_restaurant_id",
        "customer_orders",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_customer_orders_dining_session_token",
        "customer_orders",
        type_="foreignkey",
    )

    # Restore original dining_session foreign key
    op.create_foreign_key(
        op.f("customer_orders_dining_session_token_fkey"),
        "customer_orders",
        "dining_sessions",
        ["dining_session_token"],
        ["session_token"],
        ondelete="CASCADE",
    )

    # Remove restaurant index and column
    op.drop_index(
        op.f("ix_customer_orders_restaurant_id"),
        table_name="customer_orders",
    )

    op.drop_column("customer_orders", "restaurant_id")

    # Restore original menu_item foreign key
    op.drop_constraint(
        "fk_customer_order_items_menu_item_id",
        "customer_order_items",
        type_="foreignkey",
    )

    op.create_foreign_key(
        op.f("customer_order_items_menu_item_id_fkey"),
        "customer_order_items",
        "menu_items",
        ["menu_item_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Remove new subtotal column
    op.drop_column("customer_orders", "subtotal")
