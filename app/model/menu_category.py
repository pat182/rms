from datetime import datetime

from .menu_item import MenuItem
from .menu import Menu
from ..core.database import Base

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func,Text
from sqlalchemy.orm import Mapped, mapped_column,relationship

class MenuCategory(Base):
    __tablename__ = 'menu_categories'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    menu_id: Mapped[int] = mapped_column(
        ForeignKey(
            "menus.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("menu_categories.id"),
        nullable=True
    )

    category_name : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    sort_order: Mapped[int] = mapped_column(
        default=0,
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

    menu: Mapped["Menu"] = relationship(
        "Menu",
        back_populates="menu_categories"
    )
    parent: Mapped["MenuCategory | None"] = relationship(
        "MenuCategory",
        remote_side=[id],
        back_populates="subcategories"
    )

    subcategories: Mapped[list["MenuCategory"]] = relationship(
        "MenuCategory",
        back_populates="parent"
    )
    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="menu_category",
        order_by=MenuItem.sort_order.asc()
    )