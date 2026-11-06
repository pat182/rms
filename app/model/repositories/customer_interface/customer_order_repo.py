from app.core.base_repo import BaseRepo
from app.model import CustomerOrder

from sqlalchemy import select
from sqlalchemy.orm import selectinload


class CustomerOrderRepo(BaseRepo):
    # SEARCH_FIELDS = ("session_token",)
    # SORT_FIELDS = ("started_at", "closed_at", "status")

    @property
    def model(self):
        return CustomerOrder

    async def get_orders_with_items(self,session_token:str):
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





