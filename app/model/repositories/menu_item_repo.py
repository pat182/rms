from app.core.base_repo import BaseRepo
from app.model import MenuItem

from sqlalchemy import delete, select, func

class MenuItemRepository(BaseRepo):
    @property
    def model(self):
        return MenuItem

    async def delete_item(self,menu_id:int,ids:list) -> None:
        if not ids:
            return
        await self.db.execute(
            delete(self.model).where(
                self.model.menu_id == menu_id,
                self.model.id.in_(ids),
            )
        )