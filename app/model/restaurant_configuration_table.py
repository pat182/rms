from datetime import datetime, time
from ..core.database import Base

from sqlalchemy import DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RestaurantConfiguration(Base):
    __tablename__ = "restaurant_configurations"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True)

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    is_24_hours: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="configuration",
    )

    operating_hours: Mapped[list["RestaurantOperatingHours"]] = relationship(
        back_populates="configuration",
        cascade="all, delete-orphan",
    )