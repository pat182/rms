from datetime import datetime
from decimal import Decimal

from ..core.database import Base

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func,Text,Numeric
from sqlalchemy.orm import Mapped, mapped_column,relationship


class CustomerOrder(Base):
    __tablename__ = "customer_orders"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    dining_session_token: Mapped[str] = mapped_column(
        ForeignKey("dining_sessions.session_token", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending", 	#pending, preparing, ready, served, canceled
        server_default="pending",
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
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
    dining_session: Mapped["DiningSession"] = relationship(
        "DiningSession",
        back_populates="orders",
    )
    items: Mapped[list["CustomerOrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="orders",
    )