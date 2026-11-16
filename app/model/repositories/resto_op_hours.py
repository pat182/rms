from app.core.base_repo import BaseRepo

from app.model import RestaurantOperatingHours



class RestaurantOpHoursRepository(BaseRepo):
    SEARCH_FIELDS = ()
    SORT_FIELDS = ()

    @property
    def model(self):
        return RestaurantOperatingHours