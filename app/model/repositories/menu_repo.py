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

    async def modified_get_by_id(self, uuid: str | int, restaurant_id: int) ->dict | None:


        menu = await self.db.scalar(
            select(self.model)
            .options(
                selectinload(
                    Menu.menu_items.and_(
                        MenuItem.menu_category_id.is_(None)
                    )
                )
            )
            .where(self.model.id == uuid)
            .where(self.model.restaurant_id == restaurant_id)
        )
        # from app.core.logger import log_info
        # log_info("============================================")
        # # for cat in menu.menu_categories:
        # log_info("CAT",menu.__dict__)
        # log_info("============================================")
        if menu is None:
            return None

        categories = await self.get_menu_categories(menu.id)

        return {
            "id": menu.id,
            "restaurant_id": menu.restaurant_id,
            "menu_name": menu.menu_name,
            "description": menu.description,
            "is_active": menu.is_active,
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
            "menu_categories": categories,
            "menu_items": menu.menu_items,
        }

    async def get_menu_categories(self, menu_id: int):
        stmt = (
            select(MenuCategory)
            .where(
                MenuCategory.menu_id == menu_id,
                MenuCategory.parent_id.is_(None),
            )
            .options(
                selectinload(MenuCategory.menu_items),
                selectinload(MenuCategory.subcategories).selectinload(
                    MenuCategory.menu_items
                ),
            )
            .order_by(MenuCategory.sort_order.asc())
        )

        result = await self.db.scalars(stmt)
        return result.all()

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