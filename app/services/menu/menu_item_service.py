from app.model.menu_item import MenuItem
from app.schemas import CreateMenuItemRequest
from app.model import (Menu,MenuCategory)


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from fastapi import HTTPException

class MenuItemService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.model = MenuItem

    async def create_menu_item(self,menu_id : int, payload:list[CreateMenuItemRequest]):

        menu = await self.db.scalar(
            select(Menu).where(
                Menu.id == menu_id
            )
        )

        if not menu:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        menu_items = []

        for item in payload:

            if item.menu_category_id is not None:
                category = await self.db.scalar(
                    select(MenuCategory).where(
                        MenuCategory.id == item.menu_category_id,
                        MenuCategory.menu_id == menu_id
                    )
                )

                if not category:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Category {item.menu_category_id} not found"
                    )

            sort_order = item.sort_order

            if sort_order is None:
                max_sort_order = await self.db.scalar(
                    select(func.max(MenuItem.sort_order))
                    .where(
                        MenuItem.menu_id == menu_id
                    )
                )

            menu_items.append(self.model(
                menu_id=menu_id,
                menu_category_id=item.menu_category_id,
                item_name=item.item_name,
                description=item.description,
                price=item.price,
                image_url=item.image_url,
                is_available=item.is_available,
                sort_order=sort_order,
            ))

        self.db.add_all(menu_items)

        # await self.db.flush()
        await self.db.commit()

        for item in menu_items:
            await self.db.refresh(item)

        return menu_items