from datetime import datetime
from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String,DateTime,func

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    role_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
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

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role"
    )

