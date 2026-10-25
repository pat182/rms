from app.core.dependencies import get_db
from app.schemas import (CreateMenuCategoryRequest, CreateMenuCategoryResponse)
from app.services.menu.menu_category_service import MenuCategoryService

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/menus/{menu_id}/menu-categories",
    tags=["Menu Categories"]
)
# response_model=CreateMenuCategoryResponse
@router.post("/", response_model=CreateMenuCategoryResponse)
async def create_menu_category(menu_id:int,payload:list[CreateMenuCategoryRequest], db: AsyncSession = Depends(get_db)):

    menu_cat_service = MenuCategoryService(db)

    new_cat = await menu_cat_service.create_menu_category(menu_id,payload)

    return {
        "success": True,
        "data": new_cat
    }