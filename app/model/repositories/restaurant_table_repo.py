from app.core.base_repo import BaseRepo

from sqlalchemy import select

from app.model import RestaurantTable, DiningSession


class RestaurantTableRepo(BaseRepo):
    SEARCH_FIELDS = ("table_name",)
    # SORT_FIELDS = ("restaurant_name", "created_at", "updated_at")
    
    @property
    def model(self):
        return RestaurantTable

    async def get_dinning_sesh(self, session_token: str) -> DiningSession | None:
        sesh = (await self.db.execute(
            select(DiningSession)
            .where(DiningSession.session_token == session_token)
        ))

        return sesh.scalar_one_or_none()

