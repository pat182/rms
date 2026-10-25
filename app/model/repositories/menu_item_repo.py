from app.core.base_repo import BaseRepo
from app.model import MenuItem

class MenuItemRepository(BaseRepo):
    @property
    def model(self):
        return MenuItem