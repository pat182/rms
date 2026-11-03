from pygments.lexers import data

from ...core.dependencies import get_db
from ...dependencies.restaurant_dependencies import get_restaurant_table_service
from ...model import Restaurant
from ...services.restaurant import RestaurantTableService
from ...schemas.restaurant import (
    CreateRestoRequest,
    CreateRestoTableResponse,
    CreateSeshStatusRequest,
    UpdateRestoTableResponse,
)
from ...dependencies import (
    get_authenticated_user,
    get_current_restaurant
)

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException

router = APIRouter(
    prefix="/v1/restaurants/tables",
    tags=["Restaurants Tables"],
    dependencies=[Depends(get_authenticated_user),Depends(get_current_restaurant)],
)

@router.post("",response_model=CreateRestoTableResponse)
async def create_restaurant_table(
    payload : list[CreateRestoRequest],
    restaurant: Restaurant = Depends(get_current_restaurant),
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


@router.patch("/{table_id}", response_model=UpdateRestoTableResponse)
async def update_resto_table(
    table_id: int,
    payload: CreateRestoRequest,
    restaurant: Restaurant = Depends(get_current_restaurant),
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
