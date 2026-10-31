
from app.core.database import Base

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column,relationship

class Country(Base):
    __tablename__ = 'countries'
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    country_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    country_code: Mapped[str] = mapped_column(
        String(3),
        unique=True,
        nullable=False
    )
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant",
        back_populates="country"
    )
    phone_code: Mapped[str] = mapped_column(
        String(7),
        nullable=False
    )