from datetime import time
from ..core.database import Base

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Time,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RestaurantOperatingHours(Base):
    __tablename__ = "restaurant_operating_hours"

    __table_args__ = (
        UniqueConstraint(
            "configuration_id",
            "day_of_week",
            name="uq_restaurant_operating_hours_day",
        ),
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="ck_restaurant_operating_hours_day",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    configuration_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant_configurations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Monday = 0, Sunday = 6
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)

    opening_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    closing_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    is_closed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    configuration: Mapped["RestaurantConfiguration"] = relationship(
        back_populates="operating_hours"
    )