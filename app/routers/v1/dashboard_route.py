from datetime import datetime
from typing import Optional, Literal

from sqlalchemy.orm import selectinload

from ...core.dependencies import get_db
from ...dependencies import require_role

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas import PaginatedResponse
from ...schemas.customer_interface import CustomerOrderWithItemsAndSession
from ...services.restaurant import DashboardService

router = APIRouter(
    prefix = "/v1/dashboard",
    tags=["Dashboard"],
)

@router.get("/recent-orders",response_model=PaginatedResponse[CustomerOrderWithItemsAndSession])
async def index(
    restaurant=Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1),
    sort_order: Optional[Literal["asc", "desc"]] = Query(None),
    sort_by: Optional[
        Literal["created_at"]
    ] = Query(None),
    search: Optional[str] = Query(None),
    order_from: datetime | None = None,
    order_at: datetime | None = None,
):
    try:
        dashboard_service = DashboardService(db)

        data,total = await dashboard_service.get_recent_order_data(
            restaurant_id=restaurant.id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            order_from=order_from,
            order_at=order_at
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch recent orders",
        )

    return PaginatedResponse(page=page, page_size=page_size, total_items=total, data=data)

# @router.get("/order-insight",response_model=PaginatedResponse[CustomerOrderWithItemsAndSession])
# async def get_order_insight(
#     restaurant=Depends(require_role("owner")),
#     db: AsyncSession = Depends(get_db),
#     order_from: datetime | None = None,
#     order_at: datetime | None = None,
# ):
#     dashboard_service = DashboardService(db)
#     data = await dashboard_service.get_chart_data(restaurant, order_from, order_at)
#
#     return {
#         "success": True,
#         "data": data
#     }

@router.get("/order-chart")
async def get_chart(
    restaurant=Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
    order_from: datetime | None = None,
    order_at: datetime | None = None,
):
    try:
        dashboard_service = DashboardService(db)
        data = await dashboard_service.get_chart_data(restaurant,order_from,order_at)

        return {
            "success": True,
            "data": data
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch order chart data",
        )
