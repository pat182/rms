import json
from redis.asyncio import Redis

from ...core.websocket import manager
from ...core.dependencies import get_db
from ...dependencies import get_redis
from ...dependencies.customer_interface import get_or_create_dining_session, get_customer_order_service, customer_session_dependency
from ...dependencies.menu_dependencies.menu_dependecies import get_menu_service, get_menu_item_service
from ...model import DiningSession
from ...model.repositories import CustomerOrderRepo
from ...schemas.customer_interface.customer_interface_schema import CustomerOrderData
from ...schemas.menu.menu_item_schema import MenuItemData, MenuItemResponse
from ...schemas.customer_interface import CustomerCartRequest
from ...services import MenuService
from ...services.menu.menu_item_service import MenuItemService
from ...services.customer_inteface import CustomerOrderService

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

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
            "is_new" : is_new,
            "dinning_session_token" : dining_sesh.session_token,
            "restaurant_id" : restaurant.id,
            "restaurant_name" : restaurant.restaurant_name,
            "menu" : menu_data
        }
    }


@router.get("/item/{item_id}/{session_token}",response_model=MenuItemResponse)
async def get_menu_item(
    # table_qr : str,
    item_id: int,
    sesh_data : DiningSession = Depends(customer_session_dependency),
    item_service : MenuItemService = Depends(get_menu_item_service)
):

    restaurant = sesh_data.restaurant_table.restaurant

    item = await item_service.get_item(item_id, restaurant.id)

    return {
        "success" : True,
        "data": MenuItemData.model_validate(item),
    }

@router.get("/shared-cart/{session_token}")
async def get_shared_cart(
    sesh_data : DiningSession = Depends(customer_session_dependency),
    redis: Redis = Depends(get_redis),
    db : AsyncSession = Depends(get_db)

):
    dining_sesh = sesh_data

    cart_items = await redis.get(f"rms:cart:{dining_sesh.session_token}")

    order_repo = CustomerOrderRepo(db)
    orders = await order_repo.get_orders_by_session(dining_sesh.session_token)

    return {
        "success": True,
        "data": {
            "cart_items" :  json.loads(cart_items) if cart_items else [],
            "orders" : orders
        }
    }



@router.post("/orders/{session_token}")
async def create_order(
    payload: list[CustomerCartRequest],
    sesh_data : DiningSession = Depends(customer_session_dependency),
    order_service: CustomerOrderService = Depends(get_customer_order_service),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    try:

        dining_sesh= sesh_data

        order = await order_service.create_customer_order(
            payload,
            dining_sesh
        )

        await db.commit()


        await redis.delete(f"rms:cart:{dining_sesh.session_token}")

        await manager.broadcast(
            f"shared_cart:{dining_sesh.session_token}",
            jsonable_encoder({
                "event": "cart_updated",
                "data": {
                    "order" : [
                        {
                            "id" : order.id,
                            "status" : order.status,
                            "items" : [
                                {
                                    "id": item.id,
                                    "menu_item_id": item.menu_item_id,
                                    "item_name": item.item_name,
                                    "unit_price": item.unit_price,
                                    "quantity": item.quantity,
                                    "special_request": item.special_request,
                                    "subtotal": item.subtotal,
                                    "created_at": item.created_at.isoformat() if item.created_at else None,
                                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                                }
                                for item in order.items
                            ],
                            'subtotal': order.subtotal
                        }
                    ],
                    "cart_items" : []
                }
            })
        )

        await manager.broadcast(
            f"kitchen_orders:{order.restaurant_id}",
            jsonable_encoder({
                "event": "order_created",
                "data": {
                    "order": {
                        "id": order.id,
                        "table_number": dining_sesh.restaurant_table.id,
                        "status": order.status,
                        "created_at": order.created_at.isoformat() if order.created_at else None,
                        "items": [
                            {
                                "id": item.id,
                                "menu_item_id": item.menu_item_id,
                                "item_name": item.item_name,
                                "unit_price": item.unit_price,
                                "quantity": item.quantity,
                                "special_request": item.special_request,
                                "subtotal": item.subtotal,
                            }
                            for item in order.items
                        ],
                        "dining_session" : dining_sesh,
                        "subtotal": order.subtotal,
                    }
                }
            })
        )


        return {
            "success": True,
            "data": CustomerOrderData.model_validate(order),
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

# @router.patch("/orders/{session_token}/cancel/{order_id}")
# async def cancel_order(
#     order_id:int,
#     db: AsyncSession = Depends(get_db),
#     sesh_data : DiningSession = Depends(customer_session_dependency),
#     order_service: CustomerOrderService = Depends(get_customer_order_service),
# ):
#     pass