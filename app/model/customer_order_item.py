from datetime import datetime
from decimal import Decimal

from ..core.database import Base

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func,Text,Numeric
from sqlalchemy.orm import Mapped, mapped_column,relationship


class CustomerOrderItem(Base):
    __tablename__ = "customer_order_items"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    order_id: Mapped[str] = mapped_column(
        ForeignKey("customer_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        default=1,
        nullable=False
    )
    special_request: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    order: Mapped["CustomerOrder"] = relationship(
        "CustomerOrder",
        back_populates="items",
    )
    menu_item: Mapped["MenuItem"] = relationship(
        back_populates="order_items",
    )