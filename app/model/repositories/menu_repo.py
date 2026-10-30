from app.core.base_repo import BaseRepo
from app.model import Menu,MenuCategory,MenuItem

from sqlalchemy import select,update
from sqlalchemy.orm import selectinload,with_loader_criteria

class MenuRepository(BaseRepo):
    SEARCH_FIELDS = ("menu_name",)
    SORT_FIELDS = ("menu_name", "created_at", "updated_at")

    @property
    def model(self):
        return Menu

    async def modified_get_by_id(self, uuid: str | int, restaurant_id: int):
        result = await self.db.scalar(
            select(self.model)
            .options(
                # Load all categories, including subcategories
                selectinload(self.model.menu_categories)
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
            .where(self.model.id == uuid)
            .where(self.model.restaurant_id == restaurant_id)
        )

        return result

    async def deactivate_other_menus(
            self,
            restaurant_id: int,
            menu_id: int,
    ) -> None:
        await self.db.execute(
            update(self.model)
            .where(
                self.model.restaurant_id == restaurant_id,
                self.model.id != menu_id,
                self.model.is_active.is_(True),
            )
            .values(is_active=False)
        )