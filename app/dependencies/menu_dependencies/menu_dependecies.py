from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services import MenuService,MenuItemService,MenuCategoryService


def get_menu_service(
    db: AsyncSession = Depends(get_db),
) -> MenuService:
    return MenuService(db)


def get_menu_item_service(
    db: AsyncSession = Depends(get_db),
) -> MenuItemService:
    return MenuItemService(db)


def get_menu_category_service(
    db: AsyncSession = Depends(get_db),
) -> MenuCategoryService:
    return MenuCategoryService(db)