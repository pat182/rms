# from pygments.lexers import data
from typing import Optional, Literal

from ...core.dependencies import get_db
from ...dependencies.restaurant_dependencies import get_restaurant_table_service
from ...model import Restaurant,DiningSession
from ...model.repositories.restaurant_table_repo import RestaurantTableRepo
from ...schemas import PaginatedResponse
from ...services.restaurant import RestaurantTableService
from ...schemas.restaurant import (
    CreateRestoRequest,
    CreateRestoTableResponse,
    CreateSeshStatusRequest,
    UpdateRestoTableResponse, TableWithDinningSessionData, ShowRestoTableResponse,
)
from ...dependencies import (
    get_authenticated_user,
    get_current_restaurant, require_role
)

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException,Query

router = APIRouter(
    prefix="/v1/restaurant-table",
    tags=["Restaurants Tables"],
    dependencies=[
        # Depends(get_authenticated_user),
        Depends(get_current_restaurant)
    ],
)

@router.get("",response_model=PaginatedResponse[TableWithDinningSessionData])
async def index(
    restaurant=Depends(require_role("owner")),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1),
    db: AsyncSession = Depends(get_db),
    sort_by: Optional[
        Literal["table_name", "created_at", "updated_at", "has_active_session"]
    ] = Query(None),
    sort_order: Optional[Literal["asc", "desc"]] = Query(None),
    search: Optional[str] = Query(None),
):
    resto_table_repo = RestaurantTableRepo(db)

    table, total = await resto_table_repo.filter(
        page,
        page_size,
        sort_by,
        sort_order,
        search,
        restaurant.id,
        relationships=[
            resto_table_repo.model.dining_sessions.and_(
                # DiningSession.is_active.is_(True),
                # DiningSession.closed_at.is_(None),
                # DiningSession.status != "rejected",
            )
        ],
    )

    return PaginatedResponse(
        page=page,
        page_size=page_size,
        total_items=total,
        data=table,
    )


@router.post("",response_model=CreateRestoTableResponse)
async def create_restaurant_table(
    payload : list[CreateRestoRequest],
    restaurant=Depends(require_role("owner")),
    table_service: RestaurantTableService = Depends(get_restaurant_table_service),
    db: AsyncSession = Depends(get_db),

):
    try:
        tables = await table_service.create_resto_table(restaurant, payload)
        await db.commit()
        return {
            "success": True,
            "data" : tables
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create table",
        )


@router.patch("/{table_id}", response_model=UpdateRestoTableResponse)
async def update_resto_table(
    table_id: int,
    payload: CreateRestoRequest,
    restaurant=Depends(require_role("owner")),
    table_service: RestaurantTableService = Depends(get_restaurant_table_service),
    db: AsyncSession = Depends(get_db),
):
    try:
        table = await table_service.update_resto_table(
            table_id,
            payload,
            restaurant.id,
        )
        await db.commit()
        return {
            "success": True,
            "data": table,
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update restaurant table",
        )

@router.get("/{table_id}",response_model=ShowRestoTableResponse)
async def show(
    table_id: int,
    restaurant=Depends(require_role("owner")),
    table_service: RestaurantTableService = Depends(get_restaurant_table_service),
):
    try:
        table = await table_service.get_resto_table(table_id, restaurant.id)
        return {
            "success": True,
            "data": table
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch restaurant table",
        )


@router.delete("/{table_id}")
async def delete_table(
    table_id: int,
    table_service: RestaurantTableService = Depends(get_restaurant_table_service),
    restaurant=Depends(require_role("owner")),
):
    try:
        await table_service.delete_resto_table(table_id,restaurant.id)

        return {
            "success": True,
            "data" : "Restaurant table deleted successfully"
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete restaurant table",
        )


