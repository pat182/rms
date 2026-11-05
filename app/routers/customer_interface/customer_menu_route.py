from pydantic import BaseModel

from ...core.dependencies import get_db
from ...dependencies.customer_interface import get_or_create_dining_session
from ...dependencies.menu_dependencies.menu_dependecies import get_menu_service, get_menu_item_service
from ...model import DiningSession, MenuItem
from ...core.websocket import manager
from ...model.repositories import MenuItemRepository
from ...schemas.menu.menu_item_schema import MenuItemData, MenuItemResponse
from ...services import MenuService

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from ...services.menu.menu_item_service import MenuItemService

router = APIRouter(
    prefix="/customer/tables/{table_qr}",
    tags=["Customer Menu"]
)



@router.get("")
async def get_menu(
    sesh_data : tuple[DiningSession,bool] = Depends(get_or_create_dining_session),
    menu_service : MenuService = Depends(get_menu_service)
):
    dining_sesh, is_new = sesh_data
    restaurant = dining_sesh.restaurant_table.restaurant

    if is_new:
        await manager.broadcast(
                f"restaurant:{restaurant.id}",
                {
                    "event": "dining_session_created",
                    "data": {
                        "session_id": dining_sesh.id,
                        "session_token" : dining_sesh.session_token,
                        "table_name": dining_sesh.restaurant_table.table_name,
                        "is_active" : dining_sesh.is_active,
                        "started_at": (
                            dining_sesh.started_at.isoformat()
                            if dining_sesh.started_at else None
                        ),
                        "closed_at": (
                            dining_sesh.closed_at.isoformat()
                            if dining_sesh.closed_at else None
                        ),
                        "status": dining_sesh.status,
                    },
                },
            )

    menu_data = await menu_service.get_active_menu(restaurant.id)


    return {
        'success': True,
        'data': {
            "restaurant_id" : restaurant.id,
            "restaurant_name" : restaurant.restaurant_name,
            "menu" : menu_data
        }
    }


@router.get("/item/{item_id}",response_model=MenuItemResponse)
async def get_menu_item(
    # table_qr : str,
    item_id: int,
    sesh_data : tuple[DiningSession,bool] = Depends(get_or_create_dining_session),
    item_service : MenuItemService = Depends(get_menu_item_service)
):

    restaurant = sesh_data[0].restaurant_table.restaurant

    # from app.core.logger import log_info
    # log_info('=======================================')
    # log_info('MENU_DATA',menu_repo)
    # log_info('=======================================')

    item = await item_service.get_item(item_id, restaurant.id)


    return {
        "success" : True,
        "data": MenuItemData.model_validate(item),
    }

@router.post("/orders")
async def create_order(
    sesh_data : tuple[DiningSession,bool] = Depends(get_or_create_dining_session),
):
    
    return {
        "success" : True,
        "data": sesh_data,
    }
