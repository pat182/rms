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