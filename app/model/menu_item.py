from datetime import datetime
from decimal import Decimal

from app.core.database import Base

from sqlalchemy import (Boolean,DateTime,ForeignKey,Numeric,String,Text,func)

from sqlalchemy.orm import (Mapped,mapped_column,relationship)


class MenuItem(Base):
    __tablename__ = "menu_items"
    __mapper_args__ = {"eager_defaults": True}
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

    menu_category_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "menu_categories.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    item_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
        back_populates="menu_items"
    )

    menu_category: Mapped["MenuCategory | None"] = relationship(
        "MenuCategory",
        back_populates="menu_items"
    )
