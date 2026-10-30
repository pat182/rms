from app.core.base_repo import BaseRepo
from app.model import MenuCategory

from sqlalchemy import delete, select, func

class MenuCategoryRepository(BaseRepo):
    @property
    def model(self):
        return MenuCategory


    async def delete_categories(self,menu_id: int,ids: list[int]) -> None:
        if not ids:
            return

        await self.db.execute(
            delete(self.model).where(
                self.model.menu_id == menu_id,
                self.model.id.in_(ids),
            )
        )
