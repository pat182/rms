from app.core.base_repo import BaseRepo
from app.model import Restaurant

class RestaurantRepository(BaseRepo):
    @property
    def model(self):
        return Restaurant