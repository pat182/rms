
from abc import ABC, abstractmethod

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo(ABC):
    SEARCH_FIELDS: tuple[str, ...] = ("name",)
    SORT_FIELDS: tuple[str, ...] = ("id", "created_at", "updated_at")

    def __init__(self, db: AsyncSession):
        self.db = db
        self.restaurant_id = 1  # TODO: use authenticated restaurant ID

    @property
    @abstractmethod
    def model(self):
        pass

    def apply_search(self, stmt, search: str | None):
        if not search or not search.strip():
            return stmt

        search = search.strip()

        conditions = [
            getattr(self.model, field).ilike(f"%{search}%")
            for field in self.SEARCH_FIELDS
            if hasattr(self.model, field)
        ]

        if conditions:
            stmt = stmt.where(or_(*conditions))

        return stmt

    async def get_by_id(self, uuid: str | int):
        return await self.db.scalar(
            select(self.model).where(self.model.id == uuid)
        )

    async def get_model_by_list_id(self,_id:int,ids:list[int]):
        return await self.db.scalars(
            select(self.model).where(
                self.model.menu_id == _id,
                self.model.id.in_(ids),
            )
        )

    async def filter(
        self,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_order: str | None,
        search: str | None,
    ):
        page = max(1, page)
        page_size = min(max(1, page_size), 100)

        stmt = select(self.model)

        # Scope queries to the current restaurant when supported.
        if hasattr(self.model, "restaurant_id"):
            stmt = stmt.where(
                self.model.restaurant_id == self.restaurant_id
            )

        stmt = self.apply_search(stmt, search)

        if sort_by in self.SORT_FIELDS:
            sort_col = getattr(self.model, sort_by, None)

            if sort_col is not None:
                stmt = stmt.order_by(
                    sort_col.asc()
                    if sort_order == "asc"
                    else sort_col.desc()
                )

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.db.scalar(total_stmt) or 0

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.scalars(stmt)

        return result.all(), total
