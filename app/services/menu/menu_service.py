from ...model.menu import Menu

from ...schemas import (
    CreateMenuRequest, MenuDataWithRelationship, CreateCompleteMenuRequest, MenuData,
    MenuItemDataWithClientID, CompleteMenuData,UpdateCompleteMenuRequest,
    ModifiedCompleteMenuData
)
from ...model.repositories import MenuRepository, RestaurantRepository
from .menu_category_service import MenuCategoryService
from .menu_item_service import MenuItemService

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession



class MenuService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = MenuRepository(self.db)

    async def get_menu(self,menu_id:int,auth_restaurant_id:int):
        menu = await self.repo.modified_get_by_id(menu_id,auth_restaurant_id)

        if not menu:
            raise HTTPException(
                status_code=404,
                detail=f"Menu with ID {menu_id} not found"
            )

        return MenuDataWithRelationship(
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

    async def update_status(self,menu_id:int,is_active:bool,auth_restaurant_id)->MenuData:
        menu = await self.repo.get_by_id(menu_id,auth_restaurant_id)

        if not menu:
            raise HTTPException(
                status_code=404,
                detail=f"Menu with ID {menu_id} not found"
            )

        if is_active:
            await self.repo.deactivate_other_menus(
                restaurant_id=menu.restaurant_id,
                menu_id=menu.id,
            )

        menu.is_active = is_active

        await self.db.flush()

        return menu

    async def create_menu(self,payload: CreateMenuRequest, restaurant_id:int) -> Menu:

        restaurant = await RestaurantRepository(self.db).get_by_id(restaurant_id)

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
            auth_restaurant_id:int
    ):
        new_menu = await self.create_menu(payload,auth_restaurant_id)

        await self.update_status(new_menu.id,new_menu.is_active,new_menu.restaurant_id)

        menu_items = []
        categories = []

        if payload.menu_items:
            items = await item_service.create_menu_items(
                new_menu.id,
                payload.menu_items,
                auth_restaurant_id
            )

            menu_items = [
                MenuItemDataWithClientID.model_validate(item)
                for item in items
            ]


        if payload.categories:
            categories = await category_service.create_complete_menu_category(
                new_menu.id,
                payload.categories,
                item_service,
                auth_restaurant_id
            )
        return CompleteMenuData(
            **MenuData.model_validate(new_menu).model_dump(),
            categories=categories,
            menu_items=menu_items,
        )

    async def update_complete_menu(
            self,menu_id:int,
            payload: UpdateCompleteMenuRequest,
            item_service: MenuItemService,
            category_service: MenuCategoryService,
            auth_restaurant_id:int
    ):
        current_menu = await  self.repo.get_by_id(menu_id,auth_restaurant_id)
        # from app.core.logger import log_info
        # log_info("==================================")
        # log_info("PAYLOAD:", current_menu.__dict__)

        if not current_menu:
           raise HTTPException(
               status_code=404,
               detail=f"Menu with ID {menu_id} not found"
        )
        # breakpoint()
        current_menu.menu_name = payload.menu_name
        current_menu.description = payload.description

        removed = payload.removed_items
        menu_items = []
        categories = []
        # =========Prepare delete=========
        removed_item_ids = list({
            *removed.menu_item_ids,
            *removed.category_menu_item_ids,
            *removed.subcategory_menu_item_ids,
        })

        image_path = await item_service.delete_item(
            current_menu.id,
            removed_item_ids,
        )
        await category_service.delete_categories(
            current_menu.id,
            removed.subcategory_ids,
        )
        await category_service.delete_categories(
            current_menu.id,
            removed.category_ids,
        )

        # ==========+++++++++++++++=======


        if payload.menu_items:
            menu_items = await item_service.upsert_menu_item(current_menu.id, payload.menu_items)

        if payload.categories:
            categories = await category_service.upsert_complete_menu_categories(current_menu.id, payload.categories,item_service)

        # return {
        #     "menu" : current_menu,
        #     "menu_items": menu_items,
        #     "cat" : categories
        # }
        # from app.core.logger import log_info
        # log_info("==========================++++++++++++++++++++++++++++++++++++++++++++++")
        # log_info("MENU",current_menu)
        # log_info("==========================")
        # breakpoint()
        return ModifiedCompleteMenuData(
            id=current_menu.id,
            restaurant_id=current_menu.restaurant_id,
            menu_name=current_menu.menu_name,
            description=current_menu.description,
            is_active=current_menu.is_active,
            created_at=current_menu.created_at,
            updated_at=current_menu.updated_at,
            categories=categories,
            menu_items=menu_items,
            removed_image=image_path,
        )

