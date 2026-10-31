from typing import Literal, Optional

from ...core.dependencies import get_db
from ...dependencies import (
    get_authenticated_user,get_menu_service, get_menu_item_service, get_menu_category_service,get_current_restaurant
)
from ...model import User, Restaurant
from ...schemas import (
    MenuResponse,
    CreateMenuRequest,
    CreateMenuResponse,PaginatedResponse, MenuData, CreateCompleteMenuRequest, CreateCompleteMenuResponse,
    UpdateMenuStatusRequest
)
from ...model.repositories import MenuRepository
from ...schemas.menu.menu_schema_v2 import UpdateCompleteMenuRequest
from ...services import MenuService,MenuItemService,MenuCategoryService,FileStorageService


from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/menus",
    tags=["Menus"],
    dependencies=[Depends(get_authenticated_user)],
)

@router.get("",response_model=PaginatedResponse[MenuData])
async def index(
        restaurant: Restaurant = Depends(get_current_restaurant),
        page:int=Query(1,ge=1),
        page_size:int=Query(25,ge=1),
        db: AsyncSession = Depends(get_db),
        sort_by: Optional[Literal["menu_name", "created_at", "updated_at"]] = Query(None),
        sort_order: Optional[Literal["asc", "desc"]] = Query(None),
        search: Optional[str] = Query(None)
):
    menu_repo = MenuRepository(db)

    menu, total = await menu_repo.filter(page, page_size, sort_by, sort_order, search,restaurant.id)
    return PaginatedResponse(page=page, page_size=page_size, total_items=total, data=menu)

@router.get("/{menu_id}",response_model=MenuResponse)
async def get_menu(
        menu_id:int ,
        restaurant: Restaurant = Depends(get_current_restaurant),
        menu_service: MenuService = Depends(get_menu_service)
):
    try:
        menu = await menu_service.get_menu(menu_id,restaurant.id)
        return MenuResponse(
            success=True,
            data=menu
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch data",
        )


@router.patch("/{menu_id}/status",response_model=CreateMenuResponse)
async def update_status(
        menu_id: int,
        payload: UpdateMenuStatusRequest,
        db: AsyncSession = Depends(get_db),
        menu_service: MenuService = Depends(get_menu_service),
        restaurant: Restaurant = Depends(get_current_restaurant),
):

        try:

            data = await menu_service.update_status(menu_id,payload.is_active,restaurant.id)
            await db.commit()
            return CreateMenuResponse(
                success=True,
                data=data
            )
        except HTTPException:
            await db.rollback()
            raise

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to update status",
            )


@router.post("", response_model=CreateMenuResponse)
async def create_menu(
        payload: CreateMenuRequest,
        auth_user: User = Depends(get_authenticated_user),
        db: AsyncSession = Depends(get_db),
        menu_service: MenuService = Depends(get_menu_service),
        restaurant: Restaurant = Depends(get_current_restaurant)
):

    try:

        new_menu = await menu_service.create_menu(payload,restaurant.id)
        await db.commit()
        return {
            "success": True,
            "data": new_menu
        }

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create menu",
        )

@router.post("/complete", response_model=CreateCompleteMenuResponse)
async def create_menu_complete(
        payload: CreateCompleteMenuRequest,
        restaurant: Restaurant = Depends(get_current_restaurant),
        menu_service: MenuService = Depends(get_menu_service),
        db: AsyncSession = Depends(get_db),
        item_service: MenuItemService = Depends(get_menu_item_service),
        category_service: MenuCategoryService = Depends(get_menu_category_service)
):
    try:

        menu = await menu_service.create_complete_menu(payload,item_service,category_service,restaurant.id)
        await db.commit()
        return CreateCompleteMenuResponse(
                success=True,
                data=menu
        )

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create menu",
        )

@router.put("/{menu_id}/update/complete",)
async def update_complete(
        menu_id: int,
        payload : UpdateCompleteMenuRequest,
        menu_service: MenuService = Depends(get_menu_service),
        restaurant: Restaurant = Depends(get_current_restaurant),
        db: AsyncSession = Depends(get_db),
        item_service: MenuItemService = Depends(get_menu_item_service),
        category_service: MenuCategoryService = Depends(get_menu_category_service)
):
    fss = FileStorageService()

    try:
        menu = await menu_service.update_complete_menu(menu_id,payload,item_service,category_service,restaurant.id)

        await db.commit()
        for image_path in menu.removed_image:
            await fss.delete_image(image_path)

        return {
            "success": True,
            "data": menu
        }
    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update menu",
        )



