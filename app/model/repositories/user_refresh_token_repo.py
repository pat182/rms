from app.core.base_repo import BaseRepo

from app.model import UserRefreshToken
from sqlalchemy import select

class UserRefreshTokenRepository(BaseRepo):
    # SEARCH_FIELDS = ("restaurant_name",)
    # SORT_FIELDS = ("restaurant_name", "created_at", "updated_at")

    @property
    def model(self):
        return UserRefreshToken

    async def get_by_refresh_token(self, token:str):
        return await self.db.execute(
            select(self.model)
            .where(
                self.model.refresh_token == token,
            )
        )