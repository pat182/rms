from app.model.menu import Menu
from app.schemas import CreateMenuRequest,MenuDataV2
from app.model.repositories import MenuRepository, RestaurantRepository
from app.model import MenuCategory
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy import select

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
            is_active=payload.is_active or None
        )

        self.db.add(menu)

        # await self.db.flush()
        await self.db.commit()

        await self.db.refresh(menu)

        return menu