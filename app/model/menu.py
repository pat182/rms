from datetime import datetime
from app.core.database import Base

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func,Text
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.model.menu_item import MenuItem


class Menu(Base):
    __tablename__ = "menus"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=False
    )

    menu_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
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

    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="menus"
    )

    menu_categories: Mapped[list["MenuCategory"]] = relationship(
        "MenuCategory",
        back_populates="menu",
        cascade="all, delete-orphan",
    )

    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="menu",
        cascade="all, delete-orphan",
        order_by=MenuItem.sort_order.asc(),
    )

    @property
    def categories(self):
        return [
            category
            for category in self.menu_categories
            if category.parent_id is None
        ]