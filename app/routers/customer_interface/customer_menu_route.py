import json
import secrets
from redis.asyncio import Redis

from ...core.websocket import manager
from ...core.dependencies import get_db
from ...dependencies import get_redis
from ...dependencies.customer_interface import get_or_create_dining_session, get_customer_order_service, customer_session_dependency
from ...dependencies.menu_dependencies.menu_dependecies import get_menu_service, get_menu_item_service
from ...model import DiningSession
from ...model.repositories import CustomerOrderRepo
from ...schemas.menu.menu_item_schema import MenuItemData, MenuItemResponse
from ...schemas.customer_interface import CustomerCartRequest, CustomerOrderData, JoinRequestApproval
from ...services import MenuService
from ...services.menu.menu_item_service import MenuItemService
from ...services.customer_inteface import CustomerOrderService

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/customer/tables/{table_qr}",
    tags=["Customer Menu"]
)



@router.get("")
async def get_menu(
    sesh_data: tuple[DiningSession, bool, bool,bool] = Depends(get_or_create_dining_session),
    menu_service : MenuService = Depends(get_menu_service),

):
    dining_sesh, is_new, is_owner,is_approved = sesh_data
    restaurant = dining_sesh.restaurant_table.restaurant

    if is_new:
        from app.core.logger import log_info
        log_info("================================================")
        log_info("asdaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaagasdgsfdgfdgdfgfdgfd:", is_new)
        log_info("================================================")
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
            "is_approved" : is_approved,
            "is_owner": is_owner,
            "dinning_session_token": dining_sesh.session_token,
            "restaurant_id" : restaurant.id,
            "restaurant_name" : restaurant.restaurant_name,
            "menu" : menu_data,
        }
    }


@router.post("/join-request")
async def request_to_join(
    sesh_data: tuple[DiningSession, bool, bool,bool] = Depends(get_or_create_dining_session),
    device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    redis: Redis = Depends(get_redis),
):
    dining_sesh, is_new, is_owner,_ = sesh_data

    if is_owner:
        raise HTTPException(
            status_code=400,
            detail="You are already the session owner.",
        )

    request_token = secrets.token_urlsafe(16)


    request_key = (
        f"rms:dining_session:{dining_sesh.session_token}:"
        f"request:{request_token}"
    )

    # Store requesting device temporarily (5 minutes).
    await redis.set(
        request_key,
        device_token,
        ex=300,
    )

    # Notify the session owner.
    await manager.broadcast(
        f"dining_session:{dining_sesh.session_token}",
        {
            "event": "join_request",
            "data": {
                "request_token": request_token,
            },
        },
    )

    return {
        "success": True,
        "data": {
            "request_token": request_token,
            "status": "pending",
        },
    }


@router.post("/join-request/approval")
async def approve_join_request(
    table_qr: str,
    payload: JoinRequestApproval,
    device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    sesh_data: tuple[DiningSession, bool, bool,bool] = Depends(get_or_create_dining_session),
    redis: Redis = Depends(get_redis),
):
    dining_sesh, _, is_owner,_ = sesh_data

    if not is_owner:
        raise HTTPException(
            status_code=403,
            detail="Only the session owner can approve join requests.",
        )

    request_key = (
        f"rms:dining_session:{dining_sesh.session_token}:"
        f"request:{payload.request_token}"
    )

    requesting_device = await redis.get(request_key)

    if not requesting_device:
        raise HTTPException(
            status_code=404,
            detail="Join request not found or expired.",
        )

    status = "approved" if payload.approved else "rejected"

    # Grant the requesting device access for 3 hours.
    if payload.approved:
        await redis.set(
            f"rms:dining_session:{dining_sesh.session_token}:approved:{requesting_device}",
            "1",
            ex=10800,
        )

    result_key = (
        f"rms:dining_session:{dining_sesh.session_token}:"
        f"result:{payload.request_token}"
    )

    await redis.set(
        result_key,
        json.dumps({
            "status": status,
            "device_token": requesting_device,
        }),
        ex=300,
    )

    # Remove the pending request.
    await redis.delete(request_key)

    # Notify the requesting guest through their WebSocket.
    await manager.broadcast(
        f"join_request:{payload.request_token}",
        {
            "event": "join_request_result",
            "data": {
                "request_token": payload.request_token,
                "status": status,
                "session_token": (
                    dining_sesh.session_token
                    if status == "approved"
                    else None
                ),
            },
        },
    )

    return {
        "success": True,
        "data": {
            "request_token": payload.request_token,
            "status": status,
        },
    }


@router.get("/join-request/status/{request_token}")
async def get_join_request_status(
    table_qr: str,
    request_token: str,
    device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    sesh_data: tuple[DiningSession, bool, bool,bool] = Depends(get_or_create_dining_session),
    redis: Redis = Depends(get_redis),
):
    dining_sesh, _, _,_ = sesh_data

    result_key = (
        f"rms:dining_session:{dining_sesh.session_token}:"
        f"result:{request_token}"
    )

    result = await redis.get(result_key)


    if not result:
        request_key = (
            f"rms:dining_session:{dining_sesh.session_token}:"
            f"request:{request_token}"
        )

        requesting_device = await redis.get(request_key)

        if requesting_device != device_token:
            raise HTTPException(
                status_code=404,
                detail="Join request not found or expired.",
            )

        return {
            "success": True,
            "data": {
                "status": "pending",
                "session_token": None,
            },
        }

    # Verify that this device submitted the request.
    result_data = json.loads(result)

    if result_data["device_token"] != device_token:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this join request.",
        )

    status = result_data["status"]

    return {
        "success": True,
        "data": {
            "status": status,
            "session_token": (
                dining_sesh.session_token
                if status == "approved"
                else None
            ),
        },
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
    try:
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
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error, Failed to fetch cart items",
        )


@router.post("/cart/{session_token}",)
async def save_items(
    # table_qr:str,
    session_token: str,
    payload: list[CustomerCartRequest],
    redis: Redis = Depends(get_redis),
    sesh_data : DiningSession = Depends(customer_session_dependency),
):
    # dining_sesh  = sesh_data
    from app.core.logger import log_info
    log_info("====================================")
    log_info("PUKHET THAILAND")
    log_info("====================================")
    cart_data = [
        {
            **item.model_dump(mode="json"),
            "unitPrice": float(item.unitPrice)
        }
        for item in payload
    ]
    await redis.set(
        f"rms:cart:{session_token}",
        json.dumps(cart_data),
        ex=7200
    )

    await manager.broadcast(
        f"shared_cart:{session_token}",
        {
            "event": "cart_updated",
            "data": {
                "order" : [],
                "cart_items" : cart_data
            }
        }
    )

    return {
        "success" : True,
        "data" : session_token,
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


@router.patch("/orders/{session_token}/cancel/{order_id}")
async def cancel_order(
    order_id:int,
    db: AsyncSession = Depends(get_db),
    sesh_data : DiningSession = Depends(customer_session_dependency),
    order_service: CustomerOrderService = Depends(get_customer_order_service),
):
    try:

        order = await order_service.cancel_order(order_id,sesh_data.session_token)

        await db.commit()

        await manager.broadcast(
            f"kitchen_orders:{order.restaurant_id}",
            {
                "event": "dining_session_order_canceled",
                "data": {
                    "id": order.id,
                    "table_number": sesh_data.restaurant_table.id,
                    "status": order.status,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                }
            }
        )

        await manager.broadcast(
            f"customer_session:{order.dining_session_token}",
            jsonable_encoder({
                "event": "order_status_updated",
                "data": {
                    "order_id": order.id,
                    "status": order.status,
                    "cancel_reason": order.cancel_reason,
                }
            })
        )

        return {
            "success" : True,
            "data" : order
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )
