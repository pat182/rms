from typing import Literal, Optional

from app.core.dependencies import get_db
from app.schemas import (CreateMenuRequest,CreateMenuResponse,MenuResponse,PaginatedResponse,MenuData)
from app.model.repositories import MenuRepository

from app.services import MenuService
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/menus",
    tags=["Menus"]
)

@router.get("/",response_model=PaginatedResponse[MenuData])
async def index(page:int=Query(1,ge=1),
        page_size:int=Query(25,ge=1),
        db: AsyncSession = Depends(get_db),
        sort_by: Optional[Literal["menu_name", "created_at", "updated_at"]] = Query(None),
        sort_order: Optional[Literal["asc", "desc"]] = Query(None),
        search: Optional[str] = Query(None)
):
    menu_repo = MenuRepository(db)

    menu, total = await menu_repo.filter(page, page_size, sort_by, sort_order, search)

    return PaginatedResponse(page=page, page_size=page_size, total_items=total, data=menu)


@router.get("/{menu_id}",response_model=MenuResponse)
async def get_menu(menu_id:int , db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(db)

    menu = await menu_service.get_menu(menu_id)

    return MenuResponse(
        success=True,
        data=menu
    )

@router.post("/", response_model=CreateMenuResponse)
async def create_menu(payload: CreateMenuRequest, db: AsyncSession = Depends(get_db)):
    menu_service = MenuService(db)

    new_menu = await menu_service.create_menu(payload)

    return {
        "success": True,
        "data": new_menu
    }

@router.post("/complete")
async def create_menu_complete(payload: CreateMenuRequest, db: AsyncSession = Depends(get_db)):
    pass