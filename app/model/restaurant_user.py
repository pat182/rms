from datetime import datetime
from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import Boolean,ForeignKey,String,DateTime,func

class RestaurantUser(Base):
    __tablename__ = "restaurant_users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey(
            "restaurants.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
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

    restaurants: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="restaurant_users"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="restaurant_users"
    )