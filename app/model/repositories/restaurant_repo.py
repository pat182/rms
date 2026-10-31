from app.core.base_repo import BaseRepo

from app.model import Menu, Restaurant, RestaurantUser
from sqlalchemy import select

class RestaurantRepository(BaseRepo):
    SEARCH_FIELDS = ("restaurant_name",)
    SORT_FIELDS = ("restaurant_name", "created_at", "updated_at")

    @property
    def model(self):
        return Restaurant

    async def get_user_restaurant(self, restaurant_id,user_id):
        return await self.db.execute(
            select(self.model)
            .join(RestaurantUser, self.model.id == RestaurantUser.restaurant_id)
            .where(
                self.model.id == restaurant_id,
                RestaurantUser.user_id == user_id
            )
        )
    async def get_resto_by_name(self, resto_name:str ):
        return await self.db.execute(
            select(self.model).where(
                self.model.restaurant_name == resto_name
            )
        )

    async def create_restaurant_user(self,restaurant_id:int,user_id:int) -> None:

        restaurant_user = RestaurantUser(
            restaurant_id=restaurant_id,
            user_id=user_id
        )
        self.db.add(restaurant_user)