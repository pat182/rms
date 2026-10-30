from datetime import datetime

from app.core.database import Base

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship



class Restaurant(Base):
    __tablename__ = "restaurants"
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"),
        nullable=False
    )

    restaurant_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    contact_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    menus: Mapped[list["Menu"]] = relationship(
        "Menu",
        back_populates="restaurant"
    )
    restaurant_users: Mapped[list["RestaurantUser"]] = relationship(
        "RestaurantUser",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )
