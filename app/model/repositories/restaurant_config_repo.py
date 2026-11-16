
from app.core.base_repo import BaseRepo

from app.model import RestaurantConfiguration



class RestaurantConfigRepository(BaseRepo):
    SEARCH_FIELDS = ()
    SORT_FIELDS = ()

    @property
    def model(self):
        return RestaurantConfiguration

