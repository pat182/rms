from app.schemas import (CreateRestaurantRequest,CreateRestaurantResponse,RestaurantStatusRequest)
from app.services.restaurant.restaurant_service import RestaurantService
from app.core.dependencies import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/restaurants",
    tags=["Restaurants"]
)

@router.get("/{restaurant_id}",response_model=CreateRestaurantResponse)
async def show(restaurant_id: int,db: AsyncSession = Depends(get_db)):

    restaurant_service = RestaurantService(db)
    restaurant = await restaurant_service.get_restaurant(restaurant_id)

    return {
        "success": True,
        "data": restaurant
    }

@router.put("/{restaurant_id}/status",response_model=CreateRestaurantResponse)
async def toggle_status(restaurant_id: int,payload: RestaurantStatusRequest,db: AsyncSession = Depends(get_db)):
    restaurant_service = RestaurantService(db)
    restaurant = await restaurant_service.update_status(restaurant_id,payload.is_active)

    return {
        "success": True,
        "data": restaurant
    }

@router.post("/", response_model=CreateRestaurantResponse)
async def create_restaurant( payload: CreateRestaurantRequest,db: AsyncSession = Depends(get_db) ):

    restaurant_service = RestaurantService(db)
    new_restaurant = await restaurant_service.create_restaurant(payload)

    return {
        "success": True,
        "data": new_restaurant
    }

