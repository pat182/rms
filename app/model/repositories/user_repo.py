from app.core.base_repo import BaseRepo
from app.model import User,RestaurantUser

from sqlalchemy import select
from sqlalchemy.orm import selectinload

class UserRepository(BaseRepo):
    @property
    def model(self):
        return User

    async def get_by_email(self, email: str) -> User | None:
        data = await self.db.scalar(
            select(self.model)
            .options(
                selectinload(User.role),
                selectinload(User.restaurant_users)
                .selectinload(RestaurantUser.restaurant)
            )
            .where(User.email == email)
        )

        return data

    async def modified_get_by_id(self, _id: int) -> User | None:
        data = await self.db.scalar(
            select(self.model)
            .options(
                selectinload(self.model.role),
                selectinload(self.model.restaurant_users)
                .selectinload(RestaurantUser.restaurant)
            )
            .where(self.model.id == _id)
        )

        return data