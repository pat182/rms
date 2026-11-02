from app.core.base_repo import BaseRepo

from sqlalchemy import select

from app.model import RestaurantTable


class RestaurantTableRepo(BaseRepo):
    SEARCH_FIELDS = ("table_name",)
    # SORT_FIELDS = ("restaurant_name", "created_at", "updated_at")
    
    @property
    def model(self):
        return RestaurantTable

