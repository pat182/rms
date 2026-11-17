from datetime import datetime

from app.core.base_repo import BaseRepo
from app.model import CustomerOrder, DiningSession

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload


class CustomerOrderRepo(BaseRepo):
    # SEARCH_FIELDS = ("session_token",)
    # SORT_FIELDS = ("started_at", "closed_at", "status")

    @property
    def model(self):
        return CustomerOrder

    async def get_order_by_sesh(self,order_id:int, session_token:str) -> CustomerOrder | None:
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.dining_session)
            )
            .where(
                self.model.id == order_id,
                self.model.dining_session_token == session_token,
            )
        )
        result = await self.db.scalar(stmt)

        return result

    async def get_orders_by_session(self, session_token:str):
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.items),
            )
            .where(
                self.model.dining_session_token == session_token
            )
        )

        result = await self.db.scalars(stmt)
        return result.all()

    # async def get_all_orders(
    #     self,restaurant_id:int,
    #     start_date: datetime | None = None,
    #     end_date: datetime | None = None):
    #
    #     stmt = (
    #         select(self.model)
    #         .options(
    #             selectinload(self.model.items),
    #             selectinload(self.model.dining_session).selectinload(
    #                 DiningSession.restaurant_table
    #             ),
    #         )
    #         .where(
    #             self.model.restaurant_id == restaurant_id,
    #         )
    #     )
    #
    #     if start_date and end_date:
    #         stmt = stmt.where(
    #             self.model.created_at.between(start_date, end_date)
    #         )
    #
    #     stmt = stmt.order_by(self.model.created_at.asc())
    #
    #     result = await self.db.scalars(stmt)
    #
    #     return result.all()


    async def get_orders_kitchen(
            self,
            restaurant_id:int,
            start_date: datetime | None = None,
            end_date: datetime | None = None,
    ):
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.items),
                selectinload(self.model.dining_session).selectinload(
                    DiningSession.restaurant_table
                ),
            )
            .where(
                self.model.restaurant_id == restaurant_id,
                self.model.dining_session.has(
                    DiningSession.status != "closed"
                ),
            )
        )

        if start_date and end_date:
            stmt = stmt.where(
                self.model.created_at.between(start_date, end_date)
            )

        stmt = stmt.order_by(self.model.created_at.asc())

        result = await self.db.scalars(stmt)

        return result.all()

    async def get_hourly_order_counts(
            self,
            restaurant_id: int,
            order_from: datetime | None = None,
            order_at: datetime | None = None,
    ):
        hour = func.extract("hour", self.model.created_at).label("hour")

        query = (
            select(
                hour,
                func.count(self.model.id).label("orders")
            )
            .where(self.model.restaurant_id == restaurant_id)
        )

        if order_from:
            query = query.where(self.model.created_at >= order_from)

        if order_at:
            query = query.where(self.model.created_at <= order_at)

        query = query.group_by(hour).order_by(hour)

        result = await self.db.execute(query)

        return {
            int(row.hour): row.orders
            for row in result
        }






