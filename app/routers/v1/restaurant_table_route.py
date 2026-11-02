from ...core.dependencies import get_db
from ...dependencies.restaurant_dependencies import get_restaurant_table_service
from ...model import Restaurant
from ...services.restaurant import RestaurantTableService
from ...schemas.restaurant import CreateRestoRequest, CreateRestoTableResponse
from ...dependencies import (
    get_authenticated_user,
    get_current_restaurant
)

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,HTTPException

router = APIRouter(
    prefix="/v1/restaurants/tables",
    tags=["Restaurants Tables"],
    dependencies=[Depends(get_authenticated_user)],
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