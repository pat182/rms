from app.core.base_repo import BaseRepo
from app.model import Menu,MenuCategory,MenuItem

from sqlalchemy import select
from sqlalchemy.orm import selectinload,with_loader_criteria

class MenuRepository(BaseRepo):
    @property
    def model(self):
        return Menu

    async def get_by_id(self, uuid: str | int):
        result = await self.db.scalar(
            select(Menu)
            .where(Menu.id == uuid)
            .options(
                # Load all categories, including subcategories
                selectinload(Menu.menu_categories)
                .selectinload(MenuCategory.subcategories)
                .selectinload(MenuCategory.menu_items),

                selectinload(Menu.menu_categories)
                .selectinload(MenuCategory.menu_items),

                # Only load uncategorized items at menu level
                selectinload(
                    Menu.menu_items.and_(
                        MenuItem.menu_category_id.is_(None)
                    )
                ),
            )
        )

        return result