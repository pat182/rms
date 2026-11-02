from ...core.dependencies import get_db
from ...services.restaurant import RestaurantTableService

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_restaurant_table_service(db:AsyncSession=Depends(get_db))->RestaurantTableService:
    return RestaurantTableService(db)
