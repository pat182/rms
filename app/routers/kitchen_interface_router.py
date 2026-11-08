from datetime import datetime

from ..core.dependencies import get_db
from ..core.websocket import manager
from ..dependencies import require_role
from ..dependencies.customer_interface import get_customer_order_service
from ..model.repositories import CustomerOrderRepo
from ..schemas.customer_interface import GetOrdersResponse,OrderStatusRequest


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request,Query
from fastapi.encoders import jsonable_encoder



router = APIRouter(
    prefix="/kitchen",
    tags=["KITCHEN"],
)

# response_model=GetOrdersResponse
@router.get("",response_model=GetOrdersResponse)
async def get_orders(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    restaurant=Depends(require_role("owner", "manager", "kitchen")),
    db: AsyncSession = Depends(get_db)
):
    order_repo = CustomerOrderRepo(db)

    orders = await order_repo.get_orders_kitchen(
        restaurant.id,
        start_date,
        end_date
    )

    return {
        "success": True,
        "data": orders
    }

@router.patch("/{order_id}")
async def update_order_status(
    order_id: int,
    payload : OrderStatusRequest,
    db: AsyncSession = Depends(get_db),
    restaurant=Depends(require_role("owner", "manager", "kitchen")),
    order_service = Depends(get_customer_order_service)
):
    try:
        order = await order_service.update_customer_order_status(order_id, payload.status,restaurant.id)
        await db.commit()

        await manager.broadcast(
            f"customer_session:{order.dining_session_token}",
            jsonable_encoder({
                "event": "order_status_updated",
                "data": {
                    "order_id": order.id,
                    "status": order.status
                }
            })
        )

        return {
            "success": True,
            "data": order
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update status",
        )
