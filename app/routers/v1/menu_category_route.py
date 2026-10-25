from app.core.dependencies import get_db
from app.dependencies.menu_dependencies.menu_dependecies import get_menu_category_service
from app.schemas import (CreateMenuCategoryRequest, CreateMenuCategoryResponse)
from app.services.menu.menu_category_service import MenuCategoryService

from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/menus/{menu_id}/menu-categories",
    tags=["Menu Categories"]
)
@router.post("/", response_model=CreateMenuCategoryResponse)
async def create_menu_category(
        menu_id: int,payload: list[CreateMenuCategoryRequest],db: AsyncSession = Depends(get_db),
        category_service: MenuCategoryService = Depends(get_menu_category_service)
):
    try:
        async with db.begin():
            new_cat = await category_service.create_menu_category(
                menu_id,
                payload,
            )
            return CreateMenuCategoryResponse(
                success=True,
                data=new_cat
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to create menu",
        )

