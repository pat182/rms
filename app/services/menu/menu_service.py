from app.model.menu import Menu
from app.schemas import CreateMenuRequest, MenuDataV2, CreateCompleteMenuRequest, MenuItemData, MenuData
from app.model.repositories import MenuRepository, RestaurantRepository
from .menu_category_service import MenuCategoryService
from .menu_item_service import MenuItemService

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession



class MenuService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = MenuRepository(self.db)

    async def get_menu(self,menu_id:int):
        menu = await self.repo.get_by_id(menu_id)

        if not menu:
            raise HTTPException(
                status_code=404,
                detail=f"Menu with ID {menu_id} not found"
            )

        return MenuDataV2(
            id=menu.id,
            restaurant_id=menu.restaurant_id,
            menu_name=menu.menu_name,
            description=menu.description,
            is_active=menu.is_active,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
            categories=menu.categories,
            menu_items = menu.menu_items,
        )

    async def create_menu(self,payload: CreateMenuRequest) -> Menu:

        restaurant = await RestaurantRepository(self.db).get_by_id(1)

        if not restaurant:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        menu = self.repo.model(
            restaurant_id=1,
            menu_name=payload.menu_name,
            description=payload.description or None,
            is_active=payload.is_active or False
        )

        self.db.add(menu)

        await self.db.flush()

        return menu

    async def create_complete_menu(
            self,
            payload: CreateCompleteMenuRequest,
            item_service: MenuItemService,
            category_service: MenuCategoryService,
    ):
        new_menu = await self.create_menu(payload)

        menu_items = []
        categories = []

        if payload.menu_items:
            items = await item_service.create_menu_item(
                new_menu.id,
                payload.menu_items,
            )

            menu_items = [
                MenuItemData.model_validate(item)
                for item in items
            ]

        if payload.categories:
            categories = await category_service.create_complete_menu_category(
                new_menu.id,
                payload.categories,
                item_service,
            )
        return MenuDataV2(
            **MenuData.model_validate(new_menu).model_dump(),
            categories=categories,
            menu_items=menu_items,
        )
        # return {
        #     "id": new_menu.id,
        #     "restaurant_id": new_menu.restaurant_id,
        #     "menu_name": new_menu.menu_name,
        #     "description": new_menu.description,
        #     "is_active": new_menu.is_active,
        #     "created_at": new_menu.created_at,
        #     "updated_at": new_menu.updated_at,
        #     "menu_items": menu_items,
        #     "categories": categories,
        # }