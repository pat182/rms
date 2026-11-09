import uuid
from datetime import datetime

from ..core.database import Base

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship



class RestaurantTable(Base):
    __tablename__ = 'restaurant_tables'
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    table_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    capacity: Mapped[int] = mapped_column(
        nullable=False,
    )

    qr_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="tables",
    )
    dining_sessions: Mapped[list["DiningSession"]] = relationship(
        back_populates="restaurant_table",
        order_by="DiningSession.started_at.asc()",
    )

