from abc import ABC, abstractmethod
from typing import Tuple, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,or_

class BaseRepo(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @property
    @abstractmethod
    def model(self):
        pass

    async def get_by_id(self, uuid: str | int):
        data = await self.db.scalar(
            select(self.model).where(self.model.id == uuid)
        )
        return data

    def apply_search(self, stmt, search: str | None):
        if not search:
            return stmt

        return stmt.where(
            or_(
                self.model.name.ilike(f"%{search}%")
            )
        )

    async def filter(
            self,
            page: int,
            page_size: int,
            sort_by: str | None,
            sort_order: str | None,
            search: str | None
    ):
        stmt = select(self.model)

        stmt = self.apply_search(stmt, search)

        if sort_by:
            sort_col = getattr(self.model, sort_by, None)

            if sort_col is not None:
                stmt = stmt.order_by(
                    sort_col.asc()
                    if sort_order == "asc"
                    else sort_col.desc()
                )

        total_stmt = select(func.count()).select_from(
            stmt.subquery()
        )

        total = await self.db.scalar(total_stmt)

        stmt = stmt.offset(
            (page - 1) * page_size
        ).limit(page_size)

        result = await self.db.scalars(stmt)

        data = result.all()

        return data, total