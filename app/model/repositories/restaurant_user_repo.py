from app.core.base_repo import BaseRepo

from sqlalchemy import select

from app.model import RestaurantUser


class RestaurantUserRepo(BaseRepo):
    # SEARCH_FIELDS = ("table_name",)

    # SORT_FIELDS = ("restaurant_name", "created_at", "updated_at")

    @property
    def model(self):
        return RestaurantUser

    # async def get_by_user_resto_id(self, restaurant_id, user_id):
    #     return await self.db.execute(
    #             select(self.model)
    #             .where(
    #                 self.model.user_id == user_id.id
    #             )
    #             .where(
    #                 self.model.restaurant_id == restaurant_id
    #             )
    #         )

