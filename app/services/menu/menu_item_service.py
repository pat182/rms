from ...model.menu_item import MenuItem
from ...model.repositories import MenuItemRepository
from ...schemas import (
    CreateMenuItemRequest,
    MenuItemData,MenuItemDataWithClientID,UpdateCompleteMenuItemRequest
)
from ...model import (Menu,MenuCategory)
from ..file_storage_service import FileStorageService

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from fastapi import HTTPException




class MenuItemService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.model = MenuItem
        self.repo = MenuItemRepository(db)

    async def create_menu_items(
            self,
            menu_id: int,
            payload: list[CreateMenuItemRequest],
    ):
        menu = await self.db.scalar(
            select(Menu).where(Menu.id == menu_id)
        )

        if not menu:
            raise HTTPException(
                status_code=404,
                detail="Menu not found",
            )

        menu_items = []

        for item in payload:
            if item.menu_category_id is not None:
                category = await self.db.scalar(
                    select(MenuCategory).where(
                        MenuCategory.id == item.menu_category_id,
                        MenuCategory.menu_id == menu_id,
                    )
                )

                if not category:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Category {item.menu_category_id} not found",
                    )

            sort_order = item.sort_order

            if sort_order is None:
                max_sort_order = await self.db.scalar(
                    select(func.max(MenuItem.sort_order)).where(
                        MenuItem.menu_id == menu_id
                    )
                )
                sort_order = (max_sort_order or 0) + 1

            created_item = self.model(
                menu_id=menu_id,
                menu_category_id=item.menu_category_id,
                item_name=item.item_name,
                description=item.description,
                price=item.price,
                image_url=item.image_url,
                is_available=item.is_available,
                sort_order=sort_order,
            )

            menu_items.append((item.client_id, created_item))

        self.db.add_all([
            created_item
            for client_id, created_item in menu_items
        ])

        await self.db.flush()

        return [
            {
                **MenuItemData.model_validate(created_item).model_dump(),
                "client_id": client_id,
            }
            for client_id, created_item in menu_items
        ]


    async def upsert_menu_item(
        self,
        menu_id: int,
        menu_items: list[UpdateCompleteMenuItemRequest],
    )->list[MenuItemDataWithClientID]:

        if not menu_items:
            raise ValueError(
                "update_menu_item() received an empty menu_items list. "
                "Expected at least one menu item."
            )

        existing_ids = [
            item.id for item in menu_items
            if item.id is not None
        ]

        result = await self.repo.get_model_by_list_id(menu_id, existing_ids)

        existing_items = {item.id: item for item in result.all()}

        updated_items = []

        for item_data in menu_items:
            if item_data.id is not None:
                item = existing_items.get(item_data.id)

                if item is None:
                    raise ValueError(
                        f"Menu item {item_data.id} not found in menu {menu_id}"
                    )

                item.item_name = item_data.item_name
                item.description = item_data.description
                item.price = item_data.price
                item.image_url = item_data.image_url
                item.is_available = item_data.is_available
                item.sort_order = item_data.sort_order
                item.menu_category_id = item_data.menu_category_id

            else:
                item = self.model(
                    menu_id=menu_id,
                    item_name=item_data.item_name,
                    description=item_data.description,
                    price=item_data.price,
                    image_url=item_data.image_url,
                    is_available=item_data.is_available,
                    sort_order=item_data.sort_order,
                    menu_category_id=item_data.menu_category_id
                )
                self.db.add(item)

            item.client_id = item_data.client_id
            updated_items.append(item)

        await self.db.flush()

        # from app.core.logger import log_info

        # for updated_item in updated_items:
        #     log_info("==========================")
        #     log_info("ITEMS", updated_item)
        #
        #     log_info("==========================")
        return updated_items


    async def delete_item(
            self,
            menu_id: int,
            ids: list[int],
    ) -> list[str]:
        if not ids:
            return []

        result = await self.repo.get_model_by_list_id(menu_id,ids)

        image_paths = [
            item.image_url
            for item in result.all()
            if item.image_url
        ]

        await self.repo.delete_item(menu_id,ids)

        await self.db.flush()

        return image_paths

    async def delete_item_image(
            self,
            menu_id: int,
            item_id: int,
            image_url: str | None,
    ) -> MenuItemData:
        fss = FileStorageService()
        menu_item_repo = MenuItemRepository(self.db)

        menu_scalars = await menu_item_repo.get_model_by_list_id(
            menu_id, [item_id]
        )
        menu_item = menu_scalars.first()

        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item with ID {item_id} not found",
            )

        if image_url:
            menu_item.image_url = None
            await fss.delete_image(image_url)


        return MenuItemData.model_validate(
            menu_item, from_attributes=True
        )




