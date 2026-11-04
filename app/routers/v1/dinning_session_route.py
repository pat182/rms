from typing import Optional, Literal
from datetime import datetime

from ...dependencies.restaurant_dependencies import get_restaurant_table_service
from ...model import Restaurant
from ...core.dependencies import get_db
from ...dependencies import (
    get_authenticated_user,
    get_current_restaurant
)

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...model.repositories import DiningSessionRepo
from ...schemas import PaginatedResponse
from ...schemas.restaurant import CreateSeshStatusRequest, DiningSessionWithTableData
from ...services.restaurant import RestaurantTableService

router = APIRouter(
    prefix="/v1/dining-session",
    tags=["Dinning Sessions"],
    dependencies=[Depends(get_authenticated_user),Depends(get_current_restaurant)],
)

@router.get("",response_model=PaginatedResponse[DiningSessionWithTableData])
async def dining_sesh_index(
    restaurant: Restaurant = Depends(get_current_restaurant),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1),

    sort_by: Optional[
        Literal["started_at", "closed_at", "status"]
    ] = Query(None),
    sort_order: Optional[Literal["asc", "desc"]] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = None,
    status: Optional[Literal["verified", "pending","closed"]] = None,
    started_from: datetime | None = Query(None),
    started_to: datetime | None = Query(None),

    db: AsyncSession = Depends(get_db),
):

    dining_sesh_repo = DiningSessionRepo(db)

    filters = []

    if is_active is not None:
        filters.append(
            dining_sesh_repo.model.is_active == is_active
        )
    if status is not None:
        filters.append(
            dining_sesh_repo.model.status == status
        )

    if started_from is not None:
        filters.append(
            dining_sesh_repo.model.started_at >= started_from
        )

    if started_to is not None:
        filters.append(
            dining_sesh_repo.model.started_at <= started_to
        )

        # Validate date range
    if started_from is not None and started_to is not None and started_from > started_to:
        raise HTTPException(
            status_code=422,
            detail="'_from' must not be later than '_to'.",
        )

    dining_sesh, total = await dining_sesh_repo.filter(
        page,
        page_size,
        sort_by,
        sort_order,
        search,
        restaurant.id,
        relationships=[
            dining_sesh_repo.model.restaurant_table
        ],
        filters=filters,
    )

    return PaginatedResponse(page=page, page_size=page_size, total_items=total, data=dining_sesh)

@router.patch("/{session_token}/status",)
async def update_dinning_sesh_status(
        session_token: str,
        payload : CreateSeshStatusRequest,
        table_service: RestaurantTableService = Depends(get_restaurant_table_service),
        db: AsyncSession = Depends(get_db),
):
    try:
        dining_sesh = await table_service.update_table_sesh_status(
            session_token,
            payload,
        )
        await db.commit()

        return {
            "success": True,
            "data": dining_sesh,
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update dining session status",
        )
