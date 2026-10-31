from datetime import datetime
from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import Boolean,ForeignKey,String,DateTime,func


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users"
    )
    restaurant_users: Mapped[list["RestaurantUser"]] = relationship(
        "RestaurantUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped["UserRefreshToken"] = relationship(
        "UserRefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # @property
    # def restaurants(self):
    #     return [
    #         ru.restaurant
    #         for ru in self.restaurant_users
    #         if ru.restaurant
    #     ]